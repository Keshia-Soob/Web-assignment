import flet as ft

ORANGE = ft.Colors.ORANGE


def LoginScreen(page, api, auth, go_menu):

    email = ft.TextField(label="Email", prefix_icon=ft.Icons.EMAIL)
    password = ft.TextField(label="Password", password=True, can_reveal_password=True)

    status = ft.Text()
    loading = ft.ProgressBar(visible=False)

    def login(e):
        loading.visible = True
        status.value = ""
        page.update()

        data, code = api.login(email.value, password.value)

        loading.visible = False

        if code == 200 and api.token:
            auth.save_token(api.token, email.value)
            go_menu()
        else:
            status.value = data.get("error", "Login failed")

        page.update()

    def go_register(e):
        page.go("/register")

    return ft.View(
        route="/login",
        controls=[
            ft.Container(
                padding=30,
                content=ft.Column(
                    [
                        ft.Text("Login", size=30, weight=ft.FontWeight.BOLD),

                        email,
                        password,

                        loading,
                        status,

                        ft.ElevatedButton(
                            "Login",
                            bgcolor=ORANGE,
                            color=ft.Colors.WHITE,
                            on_click=login
                        ),

                        ft.TextButton(
                            "No account? Register",
                            on_click=go_register
                        )
                    ],
                    spacing=15
                )
            )
        ]
    )