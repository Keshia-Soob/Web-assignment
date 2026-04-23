# screens/cart_screen.py
import threading
import flet as ft

from components.shared import app_bar, spinner, err_banner, bottom_nav, ORANGE

RED   = ft.Colors.RED_400
GREY  = ft.Colors.GREY_600
WHITE = ft.Colors.WHITE
BG    = ft.Colors.GREY_50


def create_cart_view(page: ft.Page, api, snack) -> ft.View:

    items_col = ft.Column(spacing=10, expand=True)
    body = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=0,
        controls=[items_col],
    )

    def _item_row(item):
        iid   = item.get("id") or item.get("item_id")
        name  = item.get("name", "Item")
        price = float(item.get("price", 0))
        qty   = int(item.get("quantity", 1))
        raw   = item.get("image") or item.get("image_url")
        img_src = (
            raw if raw and raw.startswith("http")
            else f"http://127.0.0.1:8000/{raw.lstrip('/')}" if raw
            else "https://picsum.photos/seed/food/80/80"
        )

        def _inc(_):
            threading.Thread(target=lambda: (api.add_to_cart(iid), load_cart()), daemon=True).start()

        def _dec(_):
            if qty <= 1:
                threading.Thread(target=lambda: (api.remove_from_cart(iid), load_cart()), daemon=True).start()
            else:
                threading.Thread(target=lambda: (api.decrease_cart_item(iid), load_cart()), daemon=True).start()

        def _del(_):
            snack(f"Removed {name}")
            threading.Thread(target=lambda: (api.remove_from_cart(iid), load_cart()), daemon=True).start()

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Image(src=img_src, width=70, height=70, fit="cover"),
                    width=70, height=70,
                    border_radius=12,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                ),
                ft.Column([
                    ft.Text(name, size=15, weight=ft.FontWeight.W_600,
                            max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"Rs {price:.0f} each", size=12, color=GREY),
                    ft.Text(f"Rs {price * qty:.0f}", size=14,
                            weight=ft.FontWeight.BOLD, color=ORANGE),
                ], spacing=2, expand=True),
                ft.Column([
                    ft.Row([
                        ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE,
                                      icon_color=ORANGE, icon_size=22, on_click=_dec),
                        ft.Text(str(qty), size=16, weight=ft.FontWeight.BOLD,
                                width=26, text_align=ft.TextAlign.CENTER),
                        ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE,
                                      icon_color=ORANGE, icon_size=22, on_click=_inc),
                    ], spacing=0),
                    ft.TextButton("Remove", style=ft.ButtonStyle(color=RED),
                                  on_click=_del, height=28),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=WHITE,
            border_radius=16,
            padding=ft.padding.all(12),
            margin=ft.margin.symmetric(horizontal=12, vertical=4),
            shadow=ft.BoxShadow(
                blur_radius=6,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                offset=ft.Offset(0, 1),
            ),
        )

    def load_cart():
        items_col.controls.clear()
        items_col.controls.append(
            ft.Container(content=spinner(), alignment=ft.Alignment(0, 0),
                         padding=ft.padding.only(top=60))
        )
        page.update()

        cart, code = api.get_cart()
        items_col.controls.clear()

        if code != 200 or not isinstance(cart, dict):
            items_col.controls.append(
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
                    "image":    v.get("image") or v.get("image_url"),
                }
                for k, v in items.items()
            ]

        if not items:
            items_col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("🛒", size=72),
                        ft.Text("Your cart is empty", size=22,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                        ft.Text("Add some delicious meals from the menu!",
                                size=14, color=GREY, text_align=ft.TextAlign.CENTER),
                        ft.ElevatedButton(
                            "Explore Menu",
                            icon=ft.Icons.RESTAURANT_MENU,
                            style=ft.ButtonStyle(
                                bgcolor=ORANGE, color=WHITE,
                                shape=ft.RoundedRectangleBorder(radius=25),
                            ),
                            on_click=lambda _: page.go("/menu"),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
                    padding=ft.padding.symmetric(vertical=80, horizontal=24),
                    alignment=ft.Alignment(0, 0),
                )
            )
            page.update()
            return

        # Header
        items_col.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, color=ORANGE, size=22),
                    ft.Text("Your Cart", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Text(str(len(items)), size=12, color=WHITE,
                                        weight=ft.FontWeight.BOLD),
                        bgcolor=ORANGE, border_radius=20,
                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                    ),
                ], spacing=8),
                padding=ft.padding.only(left=16, top=16, right=16, bottom=8),
            )
        )

        for item in items:
            items_col.controls.append(_item_row(item))

        # Checkout button
        items_col.controls.append(
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOCK_OUTLINE, color=WHITE, size=18),
                        ft.Text("Proceed to Checkout", color=WHITE,
                                size=16, weight=ft.FontWeight.BOLD),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                    style=ft.ButtonStyle(
                        bgcolor=ORANGE,
                        shape=ft.RoundedRectangleBorder(radius=30),
                        padding=ft.padding.symmetric(vertical=14),
                    ),
                    width=340,
                    on_click=lambda _: page.go("/orders"),
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=16),
                alignment=ft.Alignment(0, 0),
            )
        )

        page.update()

    threading.Thread(target=load_cart, daemon=True).start()

    return ft.View(
        route="/cart",
        bgcolor=BG,
        appbar=app_bar("🛒 Cart"),
        navigation_bar=bottom_nav(2, page),
        controls=[body],
    )
