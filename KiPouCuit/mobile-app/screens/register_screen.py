import flet as ft

ORANGE = ft.Colors.ORANGE


def RegisterScreen(page, api, auth, go_menu):

    first_name = ft.TextField(label="First Name")
    last_name = ft.TextField(label="Last Name")
    email = ft.TextField(label="Email")
    phone = ft.TextField(label="Phone (+230)")
    address = ft.TextField(label="Address")
    password = ft.TextField(label="Password", password=True, can_reveal_password=True)

    status = ft.Text()
    loading = ft.ProgressBar(visible=False)

    def register(e):
        loading.visible = True
        page.update()

        payload = {
            "first_name": first_name.value,
            "last_name": last_name.value,
            "email": email.value,
            "phone": phone.value,
            "address": address.value,
            "password": password.value
        }

        data, code = api._post("/auth/register/", payload)

        loading.visible = False

        if code in [200, 201]:
            api.token = data.get("token")
            auth.save_token(api.token, email.value)
            go_menu()
        else:
            status.value = data.get("error", "Registration failed")

        page.update()

    def go_login(e):
        page.go("/login")

    return ft.View(
        route="/register",
        controls=[
            ft.Container(
                padding=30,
                content=ft.Column(
                    [
                        ft.Text("Register", size=30, weight=ft.FontWeight.BOLD),

                        first_name,
                        last_name,
                        email,
                        phone,
                        address,
                        password,

                        loading,
                        status,

                        ft.ElevatedButton(
                            "Create Account",
                            bgcolor=ORANGE,
                            color=ft.Colors.WHITE,
                            on_click=register
                        ),

                        ft.TextButton(
                            "Back to Login",
                            on_click=go_login
                        )
                    ],
                    spacing=10
                )
            )
        ]
    )