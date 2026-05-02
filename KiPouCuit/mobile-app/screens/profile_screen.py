import flet as ft
import threading

from components.shared import app_bar, bottom_nav, ORANGE, CUISINE_EMOJI, spinner


def create_profile_view(page: ft.Page, api, auth) -> ft.View:


    wrapper = ft.Container(expand=True, alignment=ft.Alignment(0, 0), content=spinner())

    def logout(e):
        api.logout()
        auth.clear()
        page.go("/login")

    def load_profile():
        data, code = api.get_homecook_dashboard()

        if code == 200 and isinstance(data, dict):
            controls = _homecook_controls(data, api.username, logout)
        else:
            orders, ocode = api.get_orders()
            total = len(orders) if ocode == 200 and isinstance(orders, list) else 0
            delivered = sum(1 for o in orders if o.get("status") == "delivered") if ocode == 200 and isinstance(orders, list) else 0
            controls = _customer_controls(api.username, total, delivered, logout)

        wrapper.alignment = None
        wrapper.content = ft.Column(
            controls=controls,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        page.update()

    threading.Thread(target=load_profile, daemon=True).start()

    return ft.View(
        route="/profile",
        appbar=app_bar("👤 My Profile"),
        navigation_bar=bottom_nav(5, page),
        bgcolor=ft.Colors.GREY_50,
        controls=[wrapper],
    )
    
def _customer_controls(username, total_orders, delivered, logout):
    return [
        # Avatar
        ft.Container(
            alignment=ft.Alignment(0, 0),
            padding=ft.padding.symmetric(vertical=28),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Container(
                        bgcolor=ORANGE,
                        border_radius=50,
                        padding=14,
                        content=ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=80, color=ft.Colors.WHITE),
                    ),
                    ft.Text(username, size=21, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        bgcolor=ft.Colors.ORANGE_50,
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=14, vertical=4),
                        content=ft.Text("Customer Account", size=12, color=ORANGE, weight=ft.FontWeight.W_500),
                    ),
                ],
            ),
        ),

        ft.Container(
            padding=ft.padding.symmetric(horizontal=16, vertical=4),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    _stat_card("Orders", str(total_orders), ft.Icons.RECEIPT_LONG),
                    _stat_card("Delivered", str(delivered), ft.Icons.DONE_ALL),
                ],
            ),
        ),

        _card(
            title="Account Details",
            controls=[
                _info_row(ft.Icons.EMAIL_OUTLINED, "Email / Username", username),
                _info_row(ft.Icons.VERIFIED_USER_OUTLINED, "Account Type", "Customer"),
            ],
        ),


        _card(
            title="Quick Links",
            controls=[
                _nav_tile(ft.Icons.RESTAURANT_MENU, "Browse Menu", "Explore all available dishes", lambda e: None, route="/menu"),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                _nav_tile(ft.Icons.RECEIPT_LONG, "My Orders", "View your order history", lambda e: None, route="/orders"),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                _nav_tile(ft.Icons.STAR_BORDER, "My Reviews", "Reviews you have written", lambda e: None, route="/reviews"),
            ],
        ),


        _logout_button(logout),
    ]


def _homecook_controls(data, username, logout):
    cook = data.get("cook", {})
    my_items = data.get("my_items", [])
    available = data.get("available", [])

    name = f"{cook.get('name', '')} {cook.get('surname', '')}".strip() or username
    cuisine = cook.get("cuisine", "")
    bio = cook.get("bio", "")
    address = cook.get("address", "")
    phone = cook.get("phone", "")
    cuisine_emoji = CUISINE_EMOJI.get(cuisine, "🍽️")

    pending_orders = sum(1 for o in my_items if o.get("status") in ("pending", "accepted"))

    return [
        ft.Container(
            alignment=ft.Alignment(0, 0),
            padding=ft.padding.symmetric(vertical=28),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Container(
                        bgcolor=ORANGE,
                        border_radius=50,
                        padding=14,
                        content=ft.Icon(ft.Icons.RESTAURANT, size=80, color=ft.Colors.WHITE),
                    ),
                    ft.Text(name, size=21, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        bgcolor=ft.Colors.ORANGE_50,
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=14, vertical=4),
                        content=ft.Text(
                            f"{cuisine_emoji}  Home Cook · {cuisine.capitalize() if cuisine else 'Various'}",
                            size=12,
                            color=ORANGE,
                            weight=ft.FontWeight.W_500,
                        ),
                    ),
                ],
            ),
        ),

   
        ft.Container(
            padding=ft.padding.symmetric(horizontal=16, vertical=4),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    _stat_card("Menu Items", str(len(available)), ft.Icons.MENU_BOOK),
                    _stat_card("Active Orders", str(pending_orders), ft.Icons.RECEIPT_LONG),
                ],
            ),
        ),

        _card(
            title="Cook Details",
            controls=[
                _info_row(ft.Icons.EMAIL_OUTLINED, "Email / Username", username),
                _info_row(ft.Icons.RESTAURANT, "Cuisine", f"{cuisine_emoji}  {cuisine.capitalize()}" if cuisine else "—"),
                _info_row(ft.Icons.LOCATION_ON_OUTLINED, "Address", address or "—"),
                _info_row(ft.Icons.PHONE_OUTLINED, "Phone", phone or "—"),
                *(
                    [_info_row(ft.Icons.INFO_OUTLINE, "Bio", bio)]
                    if bio else []
                ),
            ],
        ),

   
        _card(
            title="Manage",
            controls=[
                _nav_tile(ft.Icons.RECEIPT_LONG, "Incoming Orders", "View and manage orders", lambda e: None, route="/orders"),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                _nav_tile(ft.Icons.STAR_BORDER, "Reviews", "See what customers say", lambda e: None, route="/reviews"),
            ],
        ),

     
        _logout_button(logout),
    ]

def _card(title, controls):
    return ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=ft.padding.all(16),
        margin=ft.margin.symmetric(horizontal=16, vertical=8),
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.GREY_200, offset=ft.Offset(0, 2)),
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=ORANGE),
                *controls,
            ],
        ),
    )


def _stat_card(label, value, icon):
    return ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=28, vertical=16),
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.GREY_200, offset=ft.Offset(0, 2)),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Icon(icon, color=ORANGE, size=28),
                ft.Text(value, size=22, weight=ft.FontWeight.BOLD),
                ft.Text(label, size=12, color=ft.Colors.GREY_600),
            ],
        ),
    )


def _info_row(icon, label, value):
    return ft.Container(
        bgcolor=ft.Colors.GREY_50,
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        content=ft.Row(
            spacing=12,
            controls=[
                ft.Icon(icon, color=ORANGE, size=20),
                ft.Column(
                    spacing=2,
                    expand=True,
                    controls=[
                        ft.Text(label, size=11, color=ft.Colors.GREY_500),
                        ft.Text(value, size=14, weight=ft.FontWeight.W_500),
                    ],
                ),
            ],
        ),
    )


def _nav_tile(icon, title, subtitle, on_click, route=None):
    def handle(e):
        if route:
            e.page.go(route)
        else:
            on_click(e)

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        ink=True,
        border_radius=10,
        on_click=handle,
        content=ft.Row(
            spacing=12,
            controls=[
                ft.Icon(icon, color=ORANGE, size=22),
                ft.Column(
                    spacing=2,
                    expand=True,
                    controls=[
                        ft.Text(title, size=14, weight=ft.FontWeight.W_500),
                        ft.Text(subtitle, size=12, color=ft.Colors.GREY_500),
                    ],
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400, size=20),
            ],
        ),
    )


def _logout_button(logout):
    return ft.Container(
        margin=ft.margin.symmetric(horizontal=16, vertical=20),
        content=ft.ElevatedButton(
            "Logout",
            icon=ft.Icons.LOGOUT,
            width=400,
            height=48,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_600,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=25),
            ),
            on_click=logout,
        ),
    )
