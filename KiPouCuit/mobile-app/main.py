import flet as ft

from services.api_client import ApiClient
from services.auth_service import AuthService

from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.meals_screen import create_meals_view
from screens.profile_screen import create_profile_view
from screens.nearby_screen import create_nearby_view
from screens.reviews_screen import create_reviews_view
from screens.cart_screen import create_cart_view
from screens.orders_screen import create_orders_view

def main(page: ft.Page):
    page.title = "KiPouCuit"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window.width = 390
    page.window.height = 844

    api = ApiClient()
    auth = AuthService()

    saved = auth.load_token()


    if saved:
        api.token = saved.get("token")
        api.username = saved.get("username")


    def show_snack(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()


    def go_menu():
        page.go("/menu")


    def route_change(e):
        page.views.clear()

        if page.route == "/login":
            page.views.append(LoginScreen(page, api, auth, go_menu))

        elif page.route == "/register":
            page.views.append(RegisterScreen(page, api, auth, go_menu))

        elif page.route == "/menu":
     
            if api.token:
                page.views.append(create_meals_view(page, api, show_snack))
            else:
                page.go("/login")
                return

        elif page.route == "/profile":
            if api.token:
                page.views.append(create_profile_view(page, api, auth))
            else:
                page.go("/login")
                return
        
        elif page.route == "/nearby":

            if api.token:
                page.views.append(create_nearby_view(page, api, show_snack))
            else:
                page.go("/login")
                return
            
        elif page.route == "/reviews":
                page.views.append(create_reviews_view(page, api, show_snack))

        elif page.route == "/cart":
            if api.token:
                page.views.append(create_cart_view(page, api, show_snack))
            else:
                page.go("/login")
                return

        elif page.route == "/orders":
            if api.token:
                page.views.append(create_orders_view(page, api, show_snack))
            else:
                page.go("/login")
                return

        else:
            page.views.append(LoginScreen(page, api, auth, go_menu))

        page.update()

    page.on_route_change = route_change

    page.route = "/login"
    route_change(None)


ft.app(target=main)