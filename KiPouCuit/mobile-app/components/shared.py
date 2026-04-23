# components/shared.py
import flet as ft

CUISINE_EMOJI = {
    "mauritian": "🌴",
    "indian":    "🍛",
    "french":    "🥐",
    "english":   "🫖",
    "asian":     "🥢",
}

ORANGE = ft.Colors.ORANGE_700

STATUS_COLOR = {
    "pending":    ft.Colors.ORANGE_400,
    "accepted":   ft.Colors.BLUE_400,
    "delivering": ft.Colors.PURPLE_400,
    "delivered":  ft.Colors.GREEN_600,
}

STATUS_ICON = {
    "pending":    ft.Icons.HOURGLASS_EMPTY,
    "accepted":   ft.Icons.CHECK_CIRCLE_OUTLINE,
    "delivering": ft.Icons.LOCAL_SHIPPING,
    "delivered":  ft.Icons.DONE_ALL,
}


def app_bar(title, actions=None):
    return ft.AppBar(
        title=ft.Text(title, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor=ORANGE,
        center_title=True,
        actions=actions or [],
    )


def spinner():
    return ft.Column(
        [ft.ProgressRing(), ft.Text("Loading…", color=ft.Colors.GREY_500)],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


def err_banner(msg):
    return ft.Container(
        ft.Text(f"⚠️  {msg}", color=ft.Colors.RED_900, size=13),
        bgcolor=ft.Colors.RED_50,
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        margin=ft.Margin.symmetric(horizontal=8, vertical=4),
    )


def item_card(item, on_add):
    """Menu item card — mirrors the website"""
    emoji = CUISINE_EMOJI.get(item.get("cuisine", ""), "🍽️")
    return ft.Card(
        content=ft.Container(
            ft.Column([
                ft.Row([
                    ft.Text(f"{emoji}  {item['name']}",
                            weight=ft.FontWeight.BOLD, size=15, expand=True),
                    ft.Text(f"Rs {item['price']:.0f}",
                            color=ORANGE, weight=ft.FontWeight.BOLD),
                ]),
                ft.Text(item.get("description", ""),
                        size=12, color=ft.Colors.GREY_600,
                        max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Row([
                    ft.Chip(
                        label=ft.Text(item.get("cuisine", "").capitalize(), size=11),
                        bgcolor=ft.Colors.ORANGE_100,
                    ),
                    ft.ElevatedButton(
                        "Add to Cart",
                        icon=ft.Icons.ADD_SHOPPING_CART,
                        style=ft.ButtonStyle(bgcolor=ORANGE, color=ft.Colors.WHITE),
                        height=34,
                        on_click=lambda e, i=item: on_add(i),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=6),
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
        ),
        elevation=2,
        margin=ft.Margin.symmetric(vertical=4, horizontal=8),
    )


def bottom_nav(selected, page):
    routes = ["/menu", "/nearby", "/cart", "/orders", "/reviews", "/profile"]
    destinations = [
        ft.NavigationBarDestination(icon=ft.Icons.RESTAURANT_MENU, label="Menu"),
        ft.NavigationBarDestination(icon=ft.Icons.LOCATION_ON, label="Nearby"),
        ft.NavigationBarDestination(icon=ft.Icons.SHOPPING_CART, label="Cart"),
        ft.NavigationBarDestination(icon=ft.Icons.RECEIPT_LONG, label="Orders"),
        ft.NavigationBarDestination(icon=ft.Icons.STAR_BORDER, label="Reviews"),
        ft.NavigationBarDestination(icon=ft.Icons.ACCOUNT_CIRCLE, label="Profile"),
    ]

    def on_nav_change(e):
        index = e.control.selected_index
        if index < len(routes):
            page.push_route(routes[index])

    return ft.NavigationBar(
        destinations=destinations,
        selected_index=selected,
        bgcolor=ft.Colors.WHITE,
        on_change=on_nav_change,
    )