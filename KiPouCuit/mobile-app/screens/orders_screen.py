# screens/orders_screen.py
import threading
import flet as ft

from components.shared import app_bar, spinner, err_banner, bottom_nav, ORANGE

GREEN = ft.Colors.GREEN_600
RED   = ft.Colors.RED_400
GREY  = ft.Colors.GREY_600
WHITE = ft.Colors.WHITE
BG    = ft.Colors.GREY_50


def create_orders_view(page: ft.Page, api, snack) -> ft.View:

    body = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

    # ── payment fields — defined once so values persist ───────────────────────
    f_name   = ft.TextField(
        label="Name on card",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_radius=12, border_color=ORANGE, focused_border_color=ORANGE,
    )
    f_number = ft.TextField(
        label="Card number",
        prefix_icon=ft.Icons.CREDIT_CARD,
        border_radius=12, border_color=ORANGE, focused_border_color=ORANGE,
        keyboard_type=ft.KeyboardType.NUMBER, max_length=19,
        hint_text="XXXX XXXX XXXX XXXX",
    )
    f_expiry = ft.TextField(
        label="MM / YY", border_radius=12,
        border_color=ORANGE, focused_border_color=ORANGE,
        keyboard_type=ft.KeyboardType.NUMBER, max_length=5,
        hint_text="08 / 27", expand=True,
    )
    f_cvv = ft.TextField(
        label="CVV", border_radius=12,
        border_color=ORANGE, focused_border_color=ORANGE,
        keyboard_type=ft.KeyboardType.NUMBER, max_length=3,
        hint_text="123", password=True, expand=True,
    )
    err_text = ft.Text("", color=RED, size=13)

    def _section(title, icon, controls):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=ORANGE, size=20),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                *controls,
            ], spacing=12),
            bgcolor=WHITE,
            border_radius=16,
            padding=ft.padding.all(16),
            margin=ft.margin.symmetric(horizontal=12, vertical=6),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.with_opacity(0.07, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    def _status_timeline():
        steps = [
            (ft.Icons.RECEIPT_LONG,    "Order Received",    GREEN,  True),
            (ft.Icons.RESTAURANT,      "Preparing",         ORANGE, False),
            (ft.Icons.DELIVERY_DINING, "Out for Delivery",  GREY,   False),
            (ft.Icons.HOME,            "Delivered",         GREY,   False),
        ]
        row_items = []
        for i, (icon, label, color, active) in enumerate(steps):
            row_items.append(
                ft.Column([
                    ft.Container(
                        content=ft.Icon(icon, color=WHITE, size=18),
                        bgcolor=color if active else ft.Colors.GREY_300,
                        border_radius=20, width=40, height=40,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text(label, size=10, color=color if active else GREY,
                            text_align=ft.TextAlign.CENTER, width=70),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)
            )
            if i < len(steps) - 1:
                row_items.append(
                    ft.Container(bgcolor=ft.Colors.GREY_300, width=20, height=2,
                                 margin=ft.margin.only(bottom=22))
                )
        return ft.Row(row_items, alignment=ft.MainAxisAlignment.CENTER,
                      vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _show_confirmed():
        body.controls.clear()
        body.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=90, color=GREEN),
                    ft.Text("Order Placed!", size=26, weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text("Your meal is being prepared.\nSit tight!",
                            size=15, color=GREY, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=8),
                    _status_timeline(),
                    ft.Container(height=16),
                    ft.ElevatedButton(
                        "Back to Menu",
                        icon=ft.Icons.RESTAURANT_MENU,
                        style=ft.ButtonStyle(
                            bgcolor=ORANGE, color=WHITE,
                            shape=ft.RoundedRectangleBorder(radius=25),
                        ),
                        on_click=lambda _: page.go("/menu"),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
                padding=ft.padding.symmetric(vertical=60, horizontal=24),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
        )
        page.update()

    def load_checkout():
        body.controls.clear()
        body.controls.append(
            ft.Container(content=spinner(), alignment=ft.Alignment(0, 0),
                         padding=ft.padding.only(top=60))
        )
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

        if isinstance(items, dict):
            items = [
                {
                    "item_id":  int(k),
                    "name":     v.get("name", "Item"),
                    "price":    float(v.get("price", 0)),
                    "quantity": int(v.get("quantity", 1)),
                }
                for k, v in items.items()
            ]

        if not items:
            body.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.RECEIPT_LONG, size=80, color=ft.Colors.GREY_300),
                        ft.Text("Your cart is empty", size=22,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                        ft.Text("Add items from the menu first.",
                                size=14, color=GREY, text_align=ft.TextAlign.CENTER),
                        ft.ElevatedButton(
                            "Go to Cart",
                            icon=ft.Icons.SHOPPING_CART,
                            style=ft.ButtonStyle(
                                bgcolor=ORANGE, color=WHITE,
                                shape=ft.RoundedRectangleBorder(radius=25),
                            ),
                            on_click=lambda _: page.go("/cart"),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
                    padding=ft.padding.symmetric(vertical=80, horizontal=24),
                    alignment=ft.Alignment(0, 0),
                )
            )
            page.update()
            return

        delivery = 50.0
        total    = subtotal + delivery

        def place_order(_):
            holder = f_name.value.strip()
            number = f_number.value.strip()
            expiry = f_expiry.value.strip()
            cvv    = f_cvv.value.strip()

            if not all([holder, number, expiry, cvv]):
                err_text.value = "Please fill in all payment fields."
                page.update()
                return

            if len(number.replace(" ", "")) < 12:
                err_text.value = "Invalid card number."
                page.update()
                return

            err_text.value = ""
            page.update()

            def _do():
                resp, code = api.place_order(api.username or "Customer")
                if code in (200, 201):
                    _show_confirmed()
                else:
                    msg = resp.get("error") or resp.get("detail") or "Order failed."
                    snack(f"Failed: {msg}")

            threading.Thread(target=_do, daemon=True).start()

        # Order summary section
        body.controls.append(
            _section("Order Summary", ft.Icons.RECEIPT_LONG, [
                *[
                    ft.Row([
                        ft.Text(f"{i['quantity']} x {i['name']}",
                                size=13, color=GREY, expand=True),
                        ft.Text(f"Rs {float(i['price']) * int(i['quantity']):.0f}",
                                size=13, color=GREY),
                    ])
                    for i in items
                ],
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Row([
                    ft.Text("Subtotal", size=13, color=GREY),
                    ft.Text(f"Rs {subtotal:.0f}", size=13, color=GREY),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Delivery fee", size=13, color=GREY),
                    ft.Text(f"Rs {delivery:.0f}", size=13, color=GREY),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Total", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Rs {total:.0f}", size=18,
                            weight=ft.FontWeight.BOLD, color=ORANGE),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ])
        )

        # Payment section
        body.controls.append(
            _section("Payment", ft.Icons.LOCK_OUTLINE, [
                ft.Row([
                    ft.Icon(ft.Icons.VERIFIED_USER, color=GREEN, size=14),
                    ft.Text("Secure payment", size=11, color=GREY),
                ], spacing=4),
                f_name,
                f_number,
                ft.Row([f_expiry, f_cvv], spacing=12),
                err_text,
            ])
        )

        # Place order button
        body.controls.append(
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=WHITE, size=18),
                        ft.Text("Place Order", color=WHITE, size=16,
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
                padding=ft.padding.symmetric(horizontal=16, vertical=16),
                alignment=ft.Alignment(0, 0),
            )
        )

        page.update()

    threading.Thread(target=load_checkout, daemon=True).start()

    return ft.View(
        route="/orders",
        bgcolor=BG,
        appbar=app_bar("Checkout"),
        navigation_bar=bottom_nav(3, page),
        controls=[body],
    )
