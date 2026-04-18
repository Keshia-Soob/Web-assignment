# screens/meals_screen.py
"""
MEALS / MENU SCREEN - Pretty version with natural image sizes (like website)
"""

import flet as ft
import threading

from components.shared import (
    app_bar, spinner, err_banner, 
    CUISINE_EMOJI, bottom_nav, ORANGE
)


def create_meals_view(page: ft.Page, api, snack) -> ft.View:
    
    content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)

    search_f = ft.TextField(
        hint_text="Search for delicious dishes...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=30,
        expand=True,
        height=48,
        bgcolor=ft.Colors.WHITE,
        border_color=ORANGE,
        focused_border_color=ORANGE,
    )

    cuisine_dd = ft.Dropdown(
        hint_text="All Cuisines",
        width=190,
        height=48,
        border_radius=25,
        bgcolor=ft.Colors.WHITE,
        border_color=ORANGE,
        focused_border_color=ORANGE,
        options=[ft.dropdown.Option(key="", text="🌍  All Cuisines")] + [
            ft.dropdown.Option(key=k, text=f"{v}  {k.capitalize()}")
            for k, v in CUISINE_EMOJI.items()
        ],
        on_select=lambda e: load_menu()
    )

    header = ft.Container(
        content=ft.Row([
            ft.Text("Our Menu", size=26, weight=ft.FontWeight.BOLD, color=ORANGE),
            ft.Text(" • ", color=ft.Colors.GREY_400),
            ft.Text("0 items", size=16, color=ft.Colors.GREY_600, key="item_count"),
        ]),
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
    )

    def add_to_cart(item):
        if not api.token:
            snack("⚠️ Please login first")
            return
        _, code = api.add_to_cart(item["id"])
        if code == 200:
            snack(f"✅ {item['name']} added to cart")
        else:
            snack("❌ Failed to add item")

    def load_menu(e=None):
        content.controls.clear()
        content.controls.append(spinner())
        page.update()

        items, code = api.get_menu(
            cuisine=cuisine_dd.value or None,
            search=search_f.value.strip() or None
        )

        content.controls.clear()

        if code != 200 or not isinstance(items, list):
            content.controls.append(err_banner("Could not load menu. Make sure Django is running."))
        elif not items:
            content.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.NO_FOOD, size=90, color=ft.Colors.GREY_300),
                        ft.Text("No dishes found", size=20, weight=ft.FontWeight.W_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=60,
                )
            )
        else:
            count_ctrl = page.get_control("item_count")
            if count_ctrl:
                count_ctrl.value = f"{len(items)} items"

            for item in items:
                content.controls.append(enhanced_item_card(item, add_to_cart))

        page.update()

    def enhanced_item_card(item, on_add):
        # Improved image URL handling
        raw_image = item.get("image") or item.get("image_url") or item.get("photo")
        
        if raw_image:
            if raw_image.startswith("http"):
                image_url = raw_image
            else:
                image_url = f"http://127.0.0.1:8000/{raw_image.lstrip('/')}"
        else:
            image_url = None

        # Debug print (remove after testing)
        print(f"Item: {item.get('name')} → Image: {raw_image}")

        return ft.Card(
            elevation=4,
            margin=ft.margin.symmetric(horizontal=12, vertical=8),
            content=ft.Container(
                content=ft.Column([
                    # Image with natural aspect ratio - NO forced height
                    ft.Container(
                        content=ft.Image(
                            src=image_url or "https://picsum.photos/id/292/400/250",
                            fit="cover",                    # zoom/crop where needed (same as website)
                            width=400,                      # let it fill width
                            # Do NOT set fixed height → allows natural aspect ratio
                        ),
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        border_radius=ft.border_radius.only(top_left=16, top_right=16),
                    ),
                    
                    # Details Section
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(
                                    f"{CUISINE_EMOJI.get(item.get('cuisine',''), '🍽️')} {item.get('name', '')}",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    expand=True,
                                ),
                                ft.Text(
                                    f"Rs {float(item.get('price', 0)):.0f}",
                                    size=19,
                                    weight=ft.FontWeight.BOLD,
                                    color=ORANGE,
                                ),
                            ]),
                            ft.Text(
                                item.get("description", "No description available."),
                                size=13.5,
                                color=ft.Colors.GREY_700,
                                max_lines=3,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Row([
                                ft.Chip(
                                    label=ft.Text(item.get("cuisine", "").capitalize(), size=12),
                                    bgcolor=ft.Colors.ORANGE_50,
                                ),
                                ft.ElevatedButton(
                                    "Add to Cart",
                                    icon=ft.Icons.ADD_SHOPPING_CART_OUTLINED,
                                    style=ft.ButtonStyle(
                                        bgcolor=ORANGE,
                                        color=ft.Colors.WHITE,
                                        shape=ft.RoundedRectangleBorder(radius=25),
                                    ),
                                    on_click=lambda e, i=item: on_add(i),
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ], spacing=10),
                        padding=ft.padding.all(16),
                    )
                ], spacing=0),
                border_radius=16,
            ),
        )

    search_f.on_submit = load_menu
    cuisine_dd.on_select = load_menu

    threading.Thread(target=load_menu, daemon=True).start()

    return ft.View(
        route="/menu",
        appbar=app_bar("🍽️ Menu"),
        navigation_bar=bottom_nav(0, page),
        controls=[
            header,
            ft.Container(
                content=ft.Row([search_f, cuisine_dd], spacing=12),
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
            ),
            content,
        ],
    )