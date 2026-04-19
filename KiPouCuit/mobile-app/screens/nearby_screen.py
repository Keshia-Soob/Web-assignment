# screens/nearby_screen.py
"""
Nearby HomeCook screen — interactive map edition.

Features:
  • Real interactive map via flet_map (OpenStreetMap tiles, no API key needed)
  • Live GPS via ft.Geolocator with async permission flow
  • OSRM driving route drawn between user and selected cook
  • Suggestion banner showing nearest cuisine type
  • Scrollable cook cards below the map
  • Tap a map marker → action bar appears (Get Directions / View Menu)
"""

import flet as ft
import flet_map as fm
import requests
import threading

from components.shared import (
    app_bar, spinner, err_banner,
    CUISINE_EMOJI, bottom_nav, ORANGE,
)
from services.nearby_service import get_nearby

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
TILE_URL       = "https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}"
DEFAULT_ZOOM   = 12
DEFAULT_RADIUS = 50          # km

# Mauritius centre – fallback when GPS unavailable
FALLBACK_LAT = -20.2484
FALLBACK_LNG =  57.4834


# ─────────────────────────────────────────────────────────────────────────────
# OSRM route helper  (free, no key needed)
# ─────────────────────────────────────────────────────────────────────────────
def _get_route(user_lat, user_lng, cook_lat, cook_lng):
    """Returns a list of fm.MapLatitudeLongitude points for the driving route."""
    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{user_lng},{user_lat};{cook_lng},{cook_lat}"
        f"?overview=full&geometries=geojson"
    )
    res = requests.get(url, timeout=8).json()
    coords = res["routes"][0]["geometry"]["coordinates"]
    return [fm.MapLatitudeLongitude(lat, lng) for lng, lat in coords]


# ─────────────────────────────────────────────────────────────────────────────
# Cook card (below the map)
# ─────────────────────────────────────────────────────────────────────────────
def _cook_card(cook: dict, is_nearest: bool, on_directions, on_menu) -> ft.Card:
    emoji   = cook.get("cuisine_emoji", "🍽️")
    cuisine = cook.get("cuisine_label", cook.get("cuisine", "")).capitalize()
    name    = cook.get("name", "Unknown Cook")
    dist    = cook.get("distance_km", 0)
    address = cook.get("address", "Mauritius")
    bio     = cook.get("bio", "")

    pic_url = cook.get("profile_picture")
    avatar = (
        ft.Image(src=pic_url, width=52, height=52, fit="cover",
                 border_radius=ft.BorderRadius.all(26))
        if pic_url
        else ft.Container(
            content=ft.Text(emoji, size=24),
            width=52, height=52,
            border_radius=ft.BorderRadius.all(26),
            bgcolor=ft.Colors.ORANGE_50,
            alignment=ft.Alignment(0, 0),
        )
    )

    nearest_badge = ft.Container(
        content=ft.Text("NEAREST", size=10, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
        bgcolor=ORANGE,
        border_radius=ft.BorderRadius.all(8),
        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
        visible=is_nearest,
    )

    return ft.Card(
        elevation=3 if is_nearest else 1,
        margin=ft.Margin.symmetric(horizontal=14, vertical=5),
        content=ft.Container(
            padding=ft.Padding.all(14),
            border_radius=14,
            border=ft.border.all(2, ORANGE) if is_nearest else None,
            content=ft.Column([
                ft.Row([
                    avatar,
                    ft.Container(width=12),
                    ft.Column([
                        ft.Row([
                            ft.Text(name, size=15, weight=ft.FontWeight.BOLD,
                                    expand=True),
                            nearest_badge,
                        ]),
                        ft.Text(f"{emoji}  {cuisine}", size=13,
                                color=ft.Colors.GREY_700),
                        ft.Text(f"📍 {address}", size=12,
                                color=ft.Colors.GREY_500),
                    ], expand=True, spacing=2),
                ], vertical_alignment="start"),

                ft.Text(bio, size=12, color=ft.Colors.GREY_600,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS) if bio else ft.Container(),

                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.DIRECTIONS_BIKE_OUTLINED,
                                size=15, color=ORANGE),
                        ft.Text(f" {dist} km away", size=13,
                                color=ORANGE, weight=ft.FontWeight.W_500),
                    ]),
                    ft.Row([
                        ft.OutlinedButton(
                            "Directions",
                            icon=ft.Icons.DIRECTIONS,
                            on_click=lambda e, c=cook: on_directions(c),
                        ),
                        ft.ElevatedButton(
                            "Menu",
                            icon=ft.Icons.RESTAURANT_MENU,
                            style=ft.ButtonStyle(
                                bgcolor=ORANGE,
                                color=ft.Colors.WHITE,
                            ),
                            on_click=lambda e, c=cook: on_menu(c),
                        ),
                    ], spacing=8),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=8),
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main screen factory
# ─────────────────────────────────────────────────────────────────────────────
def create_nearby_view(page: ft.Page, api, snack) -> ft.View:

    # ── shared mutable state ──────────────────────────────────────────────────
    state = {
        "user_lat":  FALLBACK_LAT,
        "user_lng":  FALLBACK_LNG,
        "cooks":     [],
        "selected":  None,
        "route":     [],      # list of fm.MapLatitudeLongitude
    }

    # ── map container (content replaced on every render) ─────────────────────
    map_ref = ft.Container(expand=True, height=320)

    # ── action bar (appears when a map marker is tapped) ─────────────────────
    action_name_text    = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
    action_cuisine_text = ft.Text("", size=12, color=ft.Colors.GREY_600)

    action_bar = ft.Container(
        visible=False,
        bgcolor=ft.Colors.WHITE,
        padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK26),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column([action_name_text, action_cuisine_text], spacing=2),
                ft.Row([
                    ft.OutlinedButton(
                        "Directions",
                        icon=ft.Icons.DIRECTIONS,
                        on_click=lambda e: _get_directions(state["selected"]),
                    ),
                    ft.ElevatedButton(
                        "View Menu",
                        icon=ft.Icons.RESTAURANT_MENU,
                        style=ft.ButtonStyle(bgcolor=ORANGE,
                                             color=ft.Colors.WHITE),
                        on_click=lambda e: snack(
                            f"Opening menu for {state['selected']['name']}"
                            if state["selected"] else ""
                        ),
                    ),
                ], spacing=8),
            ],
        ),
    )

    # ── suggestion banner ─────────────────────────────────────────────────────
    suggestion_banner = ft.Container(visible=False, bgcolor=ft.Colors.TRANSPARENT)

    # ── status text ───────────────────────────────────────────────────────────
    status_text = ft.Text(
        "Detecting your location…",
        size=13,
        color=ft.Colors.GREY_500,
        text_align="center",
    )

    # ── cook cards column ─────────────────────────────────────────────────────
    cooks_column = ft.Column(spacing=0)

    # ─────────────────────────────────────────────────────────────────────────
    # Build & render the flet_map
    # ─────────────────────────────────────────────────────────────────────────
    def _render_map():
        markers = []

        for i, cook in enumerate(state["cooks"]):
            loc   = cook.get("location", {})
            c_lat = loc.get("lat")
            c_lng = loc.get("lng")
            if c_lat is None or c_lng is None:
                continue

            emoji      = cook.get("cuisine_emoji", "🍽️")
            is_nearest = (i == 0)

            markers.append(
                fm.Marker(
                    coordinates=fm.MapLatitudeLongitude(c_lat, c_lng),
                    content=ft.Container(
                        content=ft.Text(emoji, size=16,
                                        weight=ft.FontWeight.BOLD),
                        bgcolor=ORANGE if is_nearest else ft.Colors.WHITE,
                        border_radius=ft.BorderRadius.all(20),
                        padding=ft.Padding.all(6),
                        shadow=ft.BoxShadow(blur_radius=6,
                                            color=ft.Colors.BLACK38),
                        ink=True,
                        on_click=lambda e, c=cook: _on_marker_tap(c),
                    ),
                )
            )

        # User marker
        markers.append(
            fm.Marker(
                coordinates=fm.MapLatitudeLongitude(
                    state["user_lat"], state["user_lng"]
                ),
                content=ft.Container(
                    content=ft.Icon(ft.Icons.MY_LOCATION,
                                    color=ft.Colors.WHITE, size=18),
                    bgcolor="#1976D2",
                    border_radius=ft.BorderRadius.all(20),
                    padding=ft.Padding.all(6),
                    shadow=ft.BoxShadow(blur_radius=8,
                                        color=ft.Colors.BLACK38),
                ),
            )
        )

        layers = [
            fm.TileLayer(url_template=TILE_URL),
            fm.MarkerLayer(markers=markers),
        ]

        # Route drawn as small dot markers along the path
        if state["route"]:
            route_markers = [
                fm.Marker(
                    coordinates=pt,
                    content=ft.Container(
                        width=6, height=6,
                        bgcolor=ORANGE,
                        border_radius=ft.BorderRadius.all(3),
                    ),
                )
                for pt in state["route"]
            ]
            layers.append(fm.MarkerLayer(markers=route_markers))

        map_ref.content = fm.Map(
            expand=True,
            initial_center=fm.MapLatitudeLongitude(
                state["user_lat"], state["user_lng"]
            ),
            initial_zoom=DEFAULT_ZOOM,
            layers=layers,
        )
        page.update()

    # ─────────────────────────────────────────────────────────────────────────
    # Marker tap
    # ─────────────────────────────────────────────────────────────────────────
    def _on_marker_tap(cook: dict):
        state["selected"] = cook
        state["route"]    = []

        action_name_text.value = cook.get("name", "")
        action_cuisine_text.value = (
            f"{cook.get('cuisine_emoji', '🍽️')}  "
            f"{cook.get('cuisine_label', cook.get('cuisine', ''))}"
            f"  •  {cook.get('distance_km', '?')} km away"
        )
        action_bar.visible = True
        _render_map()

    # ─────────────────────────────────────────────────────────────────────────
    # Get directions (OSRM)
    # ─────────────────────────────────────────────────────────────────────────
    def _get_directions(cook: dict):
        if not cook:
            return
        loc   = cook.get("location", {})
        c_lat = loc.get("lat")
        c_lng = loc.get("lng")
        if c_lat is None:
            snack("No location available for this cook")
            return

        snack("⏳ Fetching route…")

        def _fetch_route():
            try:
                state["route"] = _get_route(
                    state["user_lat"], state["user_lng"], c_lat, c_lng
                )
            except Exception as ex:
                state["route"] = []
                snack(f"Route error: {ex}")
            _render_map()

        threading.Thread(target=_fetch_route, daemon=True).start()

    # ─────────────────────────────────────────────────────────────────────────
    # Fetch nearby cooks from Django
    # ─────────────────────────────────────────────────────────────────────────
    def _fetch():
        lat = state["user_lat"]
        lng = state["user_lng"]

        status_text.value = (
            f"📍 ({lat:.4f}, {lng:.4f})  •  searching {DEFAULT_RADIUS} km…"
        )
        cooks_column.controls.clear()
        cooks_column.controls.append(
            ft.Container(
                content=spinner(),
                alignment=ft.Alignment(0, 0),
                padding=ft.Padding.all(30),
            )
        )
        suggestion_banner.visible = False
        action_bar.visible        = False
        page.update()

        data, code = get_nearby(api, lat, lng, radius_km=DEFAULT_RADIUS)

        cooks_column.controls.clear()

        if code != 200 or "error" in data:
            msg = data.get("error", "Could not load nearby cooks.")
            status_text.value = f"⚠️  {msg}"
            cooks_column.controls.append(
                ft.Container(content=err_banner(msg),
                             padding=ft.Padding.all(16))
            )
            page.update()
            return

        cooks   = data.get("nearest_cooks", [])
        cuisine = data.get("suggested_cuisine", "")
        emoji   = data.get("suggested_emoji", "🍽️")

        state["cooks"]    = cooks
        state["route"]    = []
        state["selected"] = None

        status_text.value = (
            f"📍 ({lat:.4f}, {lng:.4f})  •  "
            f"{data.get('total_found', 0)} cooks within {DEFAULT_RADIUS} km"
        )

        # Suggestion banner
        if cuisine:
            suggestion_banner.visible = True
            suggestion_banner.content = ft.Container(
                margin=ft.Margin.symmetric(horizontal=14, vertical=4),
                padding=ft.Padding.all(16),
                border_radius=16,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, 0),
                    end=ft.Alignment(1, 0),
                    colors=[ORANGE, "#FF8C42"],
                ),
                content=ft.Column([
                    ft.Text("Suggested for you", size=12,
                            color=ft.Colors.WHITE70,
                            weight=ft.FontWeight.W_500),
                    ft.Text(f"{emoji}  {cuisine.capitalize()} Cuisine",
                            size=22, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE),
                    ft.Text("Based on the closest home cook near you",
                            size=12, color=ft.Colors.WHITE70),
                ], spacing=4),
            )

        # Render map with all markers
        _render_map()

        # Cook cards
        if not cooks:
            cooks_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.LOCATION_OFF_OUTLINED,
                                size=60, color=ft.Colors.GREY_300),
                        ft.Text("No cooks nearby", size=18,
                                color=ft.Colors.GREY_500),
                        ft.Text(
                            f"Try increasing radius (currently {DEFAULT_RADIUS} km)",
                            size=13, color=ft.Colors.GREY_400,
                            text_align="center",
                        ),
                    ], horizontal_alignment="center"),
                    padding=ft.Padding.symmetric(vertical=40),
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for i, cook in enumerate(cooks):
                cooks_column.controls.append(
                    _cook_card(
                        cook,
                        is_nearest=(i == 0),
                        on_directions=_get_directions,
                        on_menu=lambda c: snack(
                            f"Opening menu for {c.get('name', 'cook')}"
                        ),
                    )
                )

        page.update()

    # ─────────────────────────────────────────────────────────────────────────
    # GPS via flet-geolocator
    # overlay.append only on mobile — on desktop it renders as a red column.
    # The Geolocator object itself works on desktop without being in overlay.
    # ─────────────────────────────────────────────────────────────────────────
    _gl = None
    _is_mobile = page.platform in (
        ft.PagePlatform.ANDROID,
        ft.PagePlatform.IOS,
    )
    try:
        import flet_geolocator as ftg

        def _on_position_change(e: ftg.GeolocatorPositionChangeEvent):
            state["user_lat"] = e.position.latitude
            state["user_lng"] = e.position.longitude
            _render_map()

        _gl = ftg.Geolocator(
            configuration=ftg.GeolocatorConfiguration(
                accuracy=ftg.GeolocatorPositionAccuracy.HIGH,
            ),
            on_position_change=_on_position_change,
            on_error=lambda e: None,
        )
        if _is_mobile:
            page.overlay.append(_gl)
    except Exception:
        pass

    async def _init_gps():
        if _gl is not None:
            try:
                import flet_geolocator as ftg

                perm = await _gl.request_permission()
                granted = perm in (
                    ftg.GeolocatorPermissionStatus.ALWAYS,
                    ftg.GeolocatorPermissionStatus.WHILE_IN_USE,
                )
                if granted:
                    try:
                        pos = await _gl.get_last_known_position()
                        if pos:
                            state["user_lat"] = pos.latitude
                            state["user_lng"] = pos.longitude
                    except Exception:
                        pass
                    pos = await _gl.get_current_position()
                    state["user_lat"] = pos.latitude
                    state["user_lng"] = pos.longitude
                    status_text.value = (
                        f"✅ GPS: ({pos.latitude:.4f}, {pos.longitude:.4f})"
                    )
                else:
                    status_text.value = (
                        "⚠️ GPS permission denied – using default location"
                    )
            except Exception:
                status_text.value = "📍 Using default Mauritius location"
        else:
            status_text.value = "📍 GPS not available – using default location"

        page.update()
        threading.Thread(target=_fetch, daemon=True).start()

    page.run_task(_init_gps)

    # ─────────────────────────────────────────────────────────────────────────
    # Refresh FAB
    # ─────────────────────────────────────────────────────────────────────────
    def _on_refresh(e):
        page.run_task(_init_gps)

    # ─────────────────────────────────────────────────────────────────────────
    # Layout
    # ─────────────────────────────────────────────────────────────────────────
    body = ft.Column(
        scroll="auto",
        expand=True,
        spacing=0,
        controls=[
            ft.Container(
                content=status_text,
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                alignment=ft.Alignment(0, 0),
            ),
            suggestion_banner,
            # Interactive map
            ft.Container(
                content=map_ref,
                margin=ft.Margin.symmetric(horizontal=14, vertical=6),
                border_radius=16,
                height=320,
                clip_behavior="hardEdge",
            ),
            # Legend
            ft.Container(
                content=ft.Row([
                    ft.Container(width=12, height=12,
                                 border_radius=ft.BorderRadius.all(6),
                                 bgcolor="#1976D2"),
                    ft.Text("You", size=12, color=ft.Colors.GREY_700),
                    ft.Container(width=16),
                    ft.Container(width=12, height=12,
                                 border_radius=ft.BorderRadius.all(6),
                                 bgcolor=ORANGE),
                    ft.Text("Home cook", size=12, color=ft.Colors.GREY_700),
                ], spacing=6),
                padding=ft.Padding.symmetric(horizontal=18, vertical=2),
            ),
            # Action bar (tap a marker to reveal)
            action_bar,
            ft.Container(
                content=ft.Text("Nearby Home Cooks", size=16,
                                weight=ft.FontWeight.BOLD),
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
            ),
            cooks_column,
        ],
    )

    return ft.View(
        route="/nearby",
        appbar=app_bar("📍 Nearby"),
        navigation_bar=bottom_nav(1, page),
        bgcolor=ft.Colors.WHITE,
        padding=0,
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.REFRESH,
            bgcolor=ORANGE,
            foreground_color=ft.Colors.WHITE,
            on_click=_on_refresh,
            tooltip="Refresh location",
        ),
        controls=[
            ft.Container(
                content=body,
                expand=True,
                bgcolor=ft.Colors.WHITE,
                padding=0,
            )
        ],
    )