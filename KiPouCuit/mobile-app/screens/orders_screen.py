# screens/orders_screen.py
"""
ORDERS SCREEN - KiPouCuit Mobile App
Covers three states:
  1. Cart (order summary) – view items, adjust quantities, remove
  2. Checkout             – confirm order + enter card details
  3. Confirmed            – success splash
"""

import threading
import flet as ft

from components.shared import app_bar, spinner, err_banner, bottom_nav, ORANGE

# ─────────────────────────────────────────────────────────────────────────────
# COLOURS / STYLE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
GREEN  = ft.Colors.GREEN_600
RED    = ft.Colors.RED_400
GREY   = ft.Colors.GREY_600
LIGHT  = ft.Colors.GREY_100
WHITE  = ft.Colors.WHITE


def _card(content, padding=16, radius=16, elevation=3):
    return ft.Card(
        elevation=elevation,
        margin=ft.margin.symmetric(horizontal=12, vertical=6),
        content=ft.Container(
            content=content,
            padding=ft.padding.all(padding),
            border_radius=radius,
        ),
    )


def _divider():
    return ft.Divider(height=1, color=ft.Colors.GREY_200)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY – returns a ft.View
# ─────────────────────────────────────────────────────────────────────────────
def create_orders_view(page: ft.Page, api, snack) -> ft.View:
    """
    Single entry-point used by main.py.
    Internally renders one of three sub-screens depending on `_stage`:
      "cart"      → CartScreen
      "checkout"  → CheckoutScreen
      "confirmed" → ConfirmedScreen
    """

    # ── shared state ─────────────────────────────────────────────────────────
    _stage     = {"value": "cart"}   # mutable dict so closures can write
    _cart_data = {"items": [], "subtotal": 0.0}  # cached cart from API
    _card_info = {                   # filled during checkout
        "holder": "", "number": "", "month": "", "year": "",
        "save": True, "set_default": False,
    }

    # ── outer scrollable body ─────────────────────────────────────────────────
    body = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

    def refresh():
        """Re-render body according to current stage."""
        body.controls.clear()
        s = _stage["value"]
        if s == "cart":
            _render_cart()
        elif s == "checkout":
            _render_checkout()
        elif s == "confirmed":
            _render_confirmed()
        page.update()

    # =========================================================================
    # 1.  CART SCREEN
    # =========================================================================
    def _render_cart():
        body.controls.append(spinner())
        page.update()

        cart, code = api.get_cart()
        body.controls.clear()

        if code != 200 or not isinstance(cart, dict):
            body.controls.append(
                err_banner("Could not load cart. Make sure Django is running.")
            )
            page.update()
            return

        items    = cart.get("items") or cart.get("cart_items") or []
        subtotal = float(cart.get("subtotal") or cart.get("cart_subtotal") or 0)

        # Normalise: API may return a dict keyed by id or a list
        if isinstance(items, dict):
            items = [
                {
                    "id":       int(k),
                    "name":     v.get("name", "Item"),
                    "price":    float(v.get("price", 0)),
                    "quantity": int(v.get("quantity", 1)),
                    "image":    v.get("image") or v.get("image_url"),
                }
                for k, v in items.items()
            ]

        _cart_data["items"]    = items
        _cart_data["subtotal"] = subtotal

        # ── empty state ───────────────────────────────────────────────────────
        if not items:
            body.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("🛒", size=72),
                        ft.Text(
                            "Your cart is empty",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_700,
                        ),
                        ft.Text(
                            "Add some delicious meals from the menu!",
                            size=14,
                            color=GREY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            "Explore Menu",
                            icon=ft.Icons.RESTAURANT_MENU,
                            style=ft.ButtonStyle(
                                bgcolor=ORANGE,
                                color=WHITE,
                                shape=ft.RoundedRectangleBorder(radius=25),
                            ),
                            on_click=lambda _: page.go("/menu"),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14,
                    ),
                    padding=ft.padding.symmetric(vertical=80, horizontal=24),
                    alignment=ft.Alignment(0, 0),
                )
            )
            page.update()
            return

        # ── header ────────────────────────────────────────────────────────────
        body.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, color=ORANGE, size=24),
                    ft.Text(
                        f"Your Cart  ({len(items)} item{'s' if len(items) != 1 else ''})",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                ], spacing=8),
                padding=ft.padding.fromLTRB(16, 16, 16, 4),
            )
        )

        # ── item cards ────────────────────────────────────────────────────────
        for item in items:
            body.controls.append(_cart_item_card(item))

        # ── summary box ───────────────────────────────────────────────────────
        body.controls.append(
            _card(
                ft.Column([
                    ft.Text("Order Summary", size=16, weight=ft.FontWeight.BOLD),
                    _divider(),
                    *[
                        ft.Row([
                            ft.Text(
                                f"{i['quantity']} × {i['name']}",
                                size=13,
                                color=GREY,
                                expand=True,
                            ),
                            ft.Text(
                                f"Rs {float(i['price']) * int(i['quantity']):.0f}",
                                size=13,
                                color=GREY,
                            ),
                        ])
                        for i in items
                    ],
                    _divider(),
                    ft.Row([
                        ft.Text("Total", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"Rs {subtotal:.0f}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ORANGE,
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=8),
            )
        )

        # ── checkout button ───────────────────────────────────────────────────
        body.controls.append(
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOCK_OUTLINE, color=WHITE, size=18),
                        ft.Text("Proceed to Checkout", color=WHITE, size=16, weight=ft.FontWeight.BOLD),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                    style=ft.ButtonStyle(
                        bgcolor=ORANGE,
                        shape=ft.RoundedRectangleBorder(radius=30),
                        padding=ft.padding.symmetric(vertical=14),
                    ),
                    width=340,
                    on_click=lambda _: _go_checkout(),
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                alignment=ft.Alignment(0, 0),
            )
        )
        # page.update() is called by refresh() after _render_cart() returns

    # ── cart item card ────────────────────────────────────────────────────────
    def _cart_item_card(item):
        iid   = item["id"]
        name  = item.get("name", "Item")
        price = float(item.get("price", 0))
        qty   = int(item.get("quantity", 1))
        raw   = item.get("image") or item.get("image_url")
        img_src = (
            raw if raw and raw.startswith("http")
            else f"http://127.0.0.1:8000/{raw.lstrip('/')}" if raw
            else "https://picsum.photos/id/292/80/80"
        )

        qty_text = ft.Text(str(qty), size=16, weight=ft.FontWeight.BOLD, width=28,
                           text_align=ft.TextAlign.CENTER)

        def inc(_):
            api.add_to_cart(iid)
            threading.Thread(target=lambda: _reload_cart(), daemon=True).start()

        def dec(_):
            api.remove_from_cart(iid)
            threading.Thread(target=lambda: _reload_cart(), daemon=True).start()

        def remove(_):
            # Remove all qty by calling remove_from_cart repeatedly is wasteful;
            # instead post to the dedicated remove endpoint
            api.remove_from_cart(iid)
            snack(f"🗑️ {name} removed")
            threading.Thread(target=lambda: _reload_cart(), daemon=True).start()

        return _card(
            ft.Row([
                # Thumbnail
                ft.Container(
                    content=ft.Image(src=img_src, width=60, height=60, fit=ft.ImageFit.COVER),
                    border_radius=12,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    width=60,
                    height=60,
                ),
                # Name + price
                ft.Column([
                    ft.Text(name, size=14, weight=ft.FontWeight.W_600, max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"Rs {price:.0f} each", size=12, color=GREY),
                    ft.Text(f"Rs {price * qty:.0f}", size=14,
                            weight=ft.FontWeight.BOLD, color=ORANGE),
                ], spacing=2, expand=True),
                # Qty controls + remove
                ft.Column([
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                            icon_color=ORANGE,
                            icon_size=22,
                            on_click=dec,
                            tooltip="Decrease",
                        ),
                        qty_text,
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                            icon_color=ORANGE,
                            icon_size=22,
                            on_click=inc,
                            tooltip="Increase",
                        ),
                    ], spacing=0),
                    ft.TextButton(
                        "Remove",
                        style=ft.ButtonStyle(color=RED),
                        on_click=remove,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=12,
        )

    def _reload_cart():
        """Reload cart data and re-render cart screen."""
        _stage["value"] = "cart"
        refresh()

    # =========================================================================
    # 2.  CHECKOUT SCREEN
    # =========================================================================
    def _go_checkout():
        if not _cart_data["items"]:
            snack("⚠️ Your cart is empty!")
            return
        _stage["value"] = "checkout"
        refresh()

    def _render_checkout():
        items    = _cart_data["items"]
        subtotal = _cart_data["subtotal"]

        # ── text fields ───────────────────────────────────────────────────────
        f_holder = ft.TextField(
            label="Name on card",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=12,
            border_color=ORANGE,
            focused_border_color=ORANGE,
            value=_card_info["holder"],
        )
        f_number = ft.TextField(
            label="Card number",
            prefix_icon=ft.Icons.CREDIT_CARD,
            border_radius=12,
            border_color=ORANGE,
            focused_border_color=ORANGE,
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=19,
            value=_card_info["number"],
            hint_text="XXXX XXXX XXXX XXXX",
        )
        f_month = ft.TextField(
            label="MM",
            border_radius=12,
            border_color=ORANGE,
            focused_border_color=ORANGE,
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=2,
            value=_card_info["month"],
            expand=True,
        )
        f_year = ft.TextField(
            label="YYYY",
            border_radius=12,
            border_color=ORANGE,
            focused_border_color=ORANGE,
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=4,
            value=_card_info["year"],
            expand=True,
        )
        cb_save    = ft.Checkbox(label="Save card for next time",  value=_card_info["save"])
        cb_default = ft.Checkbox(label="Set as default card",      value=_card_info["set_default"])
        err_text   = ft.Text("", color=RED, size=13)

        # ── header ────────────────────────────────────────────────────────────
        body.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK_IOS_NEW,
                        icon_color=ORANGE,
                        on_click=lambda _: _go_back_to_cart(),
                        tooltip="Back to cart",
                    ),
                    ft.Text("Checkout", size=22, weight=ft.FontWeight.BOLD),
                ], spacing=4),
                padding=ft.padding.fromLTRB(8, 12, 16, 4),
            )
        )

        # ── order summary (read-only) ─────────────────────────────────────────
        body.controls.append(
            _card(
                ft.Column([
                    ft.Text("Order Summary", size=15, weight=ft.FontWeight.BOLD),
                    _divider(),
                    *[
                        ft.Row([
                            ft.Text(f"{i['quantity']} × {i['name']}", size=13,
                                    color=GREY, expand=True),
                            ft.Text(f"Rs {float(i['price']) * int(i['quantity']):.0f}",
                                    size=13, color=GREY),
                        ])
                        for i in items
                    ],
                    _divider(),
                    ft.Row([
                        ft.Text("Total", size=15, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Rs {subtotal:.0f}", size=17,
                                weight=ft.FontWeight.BOLD, color=ORANGE),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=8),
            )
        )

        # ── payment card form ─────────────────────────────────────────────────
        body.controls.append(
            _card(
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CREDIT_CARD, color=ORANGE),
                        ft.Text("Payment Details", size=15, weight=ft.FontWeight.BOLD),
                    ], spacing=8),
                    _divider(),
                    f_holder,
                    f_number,
                    ft.Row([f_month, f_year], spacing=12),
                    cb_save,
                    cb_default,
                    err_text,
                ], spacing=12),
            )
        )

        # ── place order button ────────────────────────────────────────────────
        def place_order(_):
            # ── validate ──────────────────────────────────────────────────────
            holder = f_holder.value.strip()
            number = f_number.value.strip()
            month  = f_month.value.strip()
            year   = f_year.value.strip()

            if not all([holder, number, month, year]):
                err_text.value = "⚠️  Please fill in all card fields."
                page.update()
                return

            try:
                m = int(month)
                y = int(year)
                if not (1 <= m <= 12):
                    raise ValueError
                if y < 2024:
                    raise ValueError
            except ValueError:
                err_text.value = "⚠️  Invalid expiry date."
                page.update()
                return

            err_text.value = ""
            page.update()

            # ── cache card info so back-navigation restores it ────────────────
            _card_info.update({
                "holder": holder, "number": number,
                "month": month, "year": year,
                "save": cb_save.value, "set_default": cb_default.value,
            })

            # ── call API ──────────────────────────────────────────────────────
            client_name = api.username or "Customer"
            resp, code = api.place_order(client_name)

            if code in (200, 201):
                _stage["value"] = "confirmed"
                refresh()
            else:
                msg = resp.get("error") or resp.get("detail") or "Order failed."
                snack(f"❌ {msg}")

        body.controls.append(
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=WHITE, size=18),
                        ft.Text("Complete Order", color=WHITE, size=16,
                                weight=ft.FontWeight.BOLD),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                    style=ft.ButtonStyle(
                        bgcolor=GREEN,
                        shape=ft.RoundedRectangleBorder(radius=30),
                        padding=ft.padding.symmetric(vertical=14),
                    ),
                    width=340,
                    on_click=place_order,
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                alignment=ft.Alignment(0, 0),
            )
        )
        # page.update() is called by refresh() after _render_checkout() returns

    def _go_back_to_cart():
        _stage["value"] = "cart"
        threading.Thread(target=lambda: refresh(), daemon=True).start()

    # =========================================================================
    # 3.  CONFIRMED SCREEN
    # =========================================================================
    def _render_confirmed():
        body.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.CHECK_CIRCLE,
                            size=100,
                            color=GREEN,
                        ),
                        margin=ft.margin.only(bottom=8),
                    ),
                    ft.Text(
                        "Order Confirmed! 🎉",
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Your delicious meal is on its way.\nSit tight and get ready to eat!",
                        size=15,
                        color=GREY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=20),
                    # Status timeline
                    _status_timeline(),
                    ft.Container(height=30),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.RESTAURANT_MENU, color=WHITE, size=18),
                            ft.Text("Back to Menu", color=WHITE, size=15,
                                    weight=ft.FontWeight.BOLD),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                        style=ft.ButtonStyle(
                            bgcolor=ORANGE,
                            shape=ft.RoundedRectangleBorder(radius=30),
                            padding=ft.padding.symmetric(vertical=14),
                        ),
                        width=280,
                        on_click=lambda _: _go_menu_after_order(),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
                ),
                padding=ft.padding.symmetric(vertical=60, horizontal=24),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
        )
        # page.update() is called by refresh() after _render_confirmed() returns

    def _status_timeline():
        steps = [
            (ft.Icons.RECEIPT_LONG,     "Order Received",    GREEN,  True),
            (ft.Icons.RESTAURANT,       "Kitchen Preparing", ORANGE, False),
            (ft.Icons.DELIVERY_DINING,  "Out for Delivery",  GREY,   False),
            (ft.Icons.HOME,             "Delivered",         GREY,   False),
        ]
        row_items = []
        for i, (icon, label, color, active) in enumerate(steps):
            row_items.append(
                ft.Column([
                    ft.Container(
                        content=ft.Icon(icon, color=WHITE, size=18),
                        bgcolor=color if active else ft.Colors.GREY_300,
                        border_radius=20,
                        width=40, height=40,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text(label, size=10, color=color if active else GREY,
                            text_align=ft.TextAlign.CENTER, width=72),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                )
            )
            if i < len(steps) - 1:
                row_items.append(
                    ft.Container(
                        bgcolor=ft.Colors.GREY_300,
                        width=24, height=2,
                        margin=ft.margin.only(bottom=22),
                    )
                )
        return ft.Row(row_items, alignment=ft.MainAxisAlignment.CENTER,
                      vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _go_menu_after_order():
        # Reset order state
        _stage["value"]        = "cart"
        _cart_data["items"]    = []
        _cart_data["subtotal"] = 0.0
        _card_info.update({"holder": "", "number": "", "month": "", "year": ""})
        page.go("/menu")

    # =========================================================================
    # INITIAL RENDER
    # =========================================================================
    threading.Thread(target=lambda: refresh(), daemon=True).start()

    return ft.View(
        route="/orders",
        appbar=app_bar("🛒 Orders"),
        navigation_bar=bottom_nav(3, page),   # index 3 = Orders tab
        controls=[body],
    )