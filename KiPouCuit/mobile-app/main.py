"""
KiPouCuit Mobile App — Modular Version (Fixed)
"""

import flet as ft

# Imports
from services.api_client import ApiClient
from components.shared import app_bar, bottom_nav, spinner, err_banner, item_card, CUISINE_EMOJI, ORANGE
from screens.meals_screen import create_meals_view

# Global API Client
api = ApiClient()

# ─────────────────────────────────────────────────────────────────────────────
#  LOGIN VIEW (kept in main.py for now)
# ─────────────────────────────────────────────────────────────────────────────
def login_view(page):
    username_f = ft.TextField(label="Username", prefix_icon=ft.Icons.PERSON, autofocus=True)
    password_f = ft.TextField(label="Password", prefix_icon=ft.Icons.LOCK, password=True, can_reveal_password=True)
    status_t   = ft.Text("", color=ft.Colors.RED_600, size=13)
    loading    = ft.ProgressBar(visible=False)

    def do_login(e):
        if not username_f.value.strip() or not password_f.value.strip():
            status_t.value = "Please enter username and password."
            page.update()
            return
        loading.visible = True
        status_t.value = ""
        page.update()

        data, code = api.login(username_f.value.strip(), password_f.value.strip())
        loading.visible = False

        if code == 200:
            page.go("/menu")
        else:
            status_t.value = data.get("error", "Login failed. Check credentials.")
        page.update()

    return ft.View(
        route="/login",
        appbar=app_bar("🍽️  KiPouCuit"),
        controls=[
            ft.Container(
                ft.Column([
                    ft.Icon(ft.Icons.RESTAURANT, size=70, color=ORANGE),
                    ft.Text("Welcome to KiPouCuit", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Text("Home-cooked Mauritian food delivered to your door",
                            color=ft.Colors.GREY_600, size=13, text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=20),
                    username_f, password_f, status_t, loading,
                    ft.ElevatedButton(
                        "Login", icon=ft.Icons.LOGIN,
                        style=ft.ButtonStyle(bgcolor=ORANGE, color=ft.Colors.WHITE),
                        width=280, on_click=do_login,
                    ),
                    ft.Text("Don't have an account? Register on the website first.",
                            color=ft.Colors.GREY_500, size=11, text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                padding=30,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main(page: ft.Page):
    page.title = "KiPouCuit"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.ORANGE)
    page.padding = 0
    page.window.width = 390
    page.window.height = 844

    def show_snack(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREY_800)
        page.snack_bar.open = True
        page.update()

    def route_change(e):
        page.views.clear()

        if page.route == "/login" or page.route == "/":
            page.views.append(login_view(page))
        elif page.route == "/menu":
            page.views.append(create_meals_view(page, api, show_snack))
        else:
            # Fallback to login if unknown route
            page.views.append(login_view(page))

        page.update()   # ← This is critical!

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            page.update()   # Important for back navigation

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Start the app properly
    page.route = "/login" if not api.token else "/menu"
    route_change(None)   # Force initial render


if __name__ == "__main__":
    ft.run(main)