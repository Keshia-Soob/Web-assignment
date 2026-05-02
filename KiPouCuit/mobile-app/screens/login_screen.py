import flet as ft

ORANGE     = "#E65100"
BG         = "#FFFFFF"   # white background
CARD_BG    = "#F7F7F7"   # very light grey card
SURFACE    = "#EFEFEF"   # field fill
TEXT_DARK  = "#1A1A1A"   # primary text
TEXT_MUTED = "#757575"   # secondary / hint text
ERROR_RED  = "#EF5350"


def LoginScreen(page, api, auth, go_menu):

    email = ft.TextField(
        label="Email address",
        hint_text="you@example.com",
        keyboard_type=ft.KeyboardType.EMAIL,
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=12,
        filled=True,
        fill_color=SURFACE,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        hint_style=ft.TextStyle(color=TEXT_MUTED),
        color=TEXT_DARK,
        border_color=SURFACE,
        focused_border_color=ORANGE,
        cursor_color=ORANGE,
        on_submit=lambda e: do_login(e),
    )

    password = ft.TextField(
        label="Password",
        hint_text="••••••••",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_radius=12,
        filled=True,
        fill_color=SURFACE,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        hint_style=ft.TextStyle(color=TEXT_MUTED),
        color=TEXT_DARK,
        border_color=SURFACE,
        focused_border_color=ORANGE,
        cursor_color=ORANGE,
        on_submit=lambda e: do_login(e),
    )

    status  = ft.Text(value="", color=ERROR_RED, size=13,
                      visible=False, text_align=ft.TextAlign.CENTER)
    loading = ft.ProgressRing(width=22, height=22, stroke_width=3,
                               color=ORANGE, visible=False)

    login_btn = ft.Button(
        content=ft.Text("Log In", size=15, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
        style=ft.ButtonStyle(
            bgcolor=ORANGE,
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding(left=0, right=0, top=14, bottom=14),
            overlay_color=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        ),
        width=305,
        on_click=lambda e: do_login(e),
    )

    def _set_loading(on: bool):
        login_btn.disabled = on
        loading.visible    = on
        status.visible     = False
        page.update()

    def _show_error(msg: str):
        status.value   = msg
        status.visible = True
        page.update()

    def do_login(e):
        email.error_text    = None
        password.error_text = None
        status.visible      = False

        if not email.value or not email.value.strip():
            email.error_text = "Email is required"
            page.update()
            return
        if not password.value:
            password.error_text = "Password is required"
            page.update()
            return

        _set_loading(True)
        data, code = api.login(email.value.strip(), password.value)
        _set_loading(False)

        if code == 200 and api.token:
            auth.save_token(api.token, email.value.strip())
            go_menu()
        else:
            _show_error(data.get("error", "Invalid email or password."))

    def go_register(e):
        page.go("/register")

    header = ft.Column(
        [
            ft.Container(
                content=ft.Icon(ft.Icons.RESTAURANT_MENU, size=52, color=ORANGE),
                bgcolor=ft.Colors.with_opacity(0.12, ORANGE),
                border_radius=20,
                padding=16,
            ),
            ft.Container(height=12),
            ft.Text("KiPouCuit", size=28, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
            ft.Text("Home-cooked meals, delivered.", size=13, color=TEXT_MUTED),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=2,
    )

    card = ft.Container(
        width=360,
        padding=ft.Padding(left=28, right=28, top=32, bottom=28),
        border_radius=20,
        bgcolor=CARD_BG,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
        shadow=ft.BoxShadow(
            blur_radius=20,
            spread_radius=0,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 4),
        ),
        content=ft.Column(
            [
                ft.Text("Welcome back", size=20,
                        weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text("Sign in to your account", size=13, color=TEXT_MUTED),
                ft.Container(height=20),

                email,
                ft.Container(height=12),
                password,
                ft.Container(height=6),

                status,
                ft.Container(height=6),

                ft.Row([login_btn, loading],
                       alignment=ft.MainAxisAlignment.CENTER, spacing=12),
                ft.Container(height=16),

                # Divider
                ft.Row(
                    [
                        ft.Container(height=1, expand=True,
                                     bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
                        ft.Text("  or  ", color=TEXT_MUTED, size=12),
                        ft.Container(height=1, expand=True,
                                     bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=12),

                # Register link
                ft.Row(
                    [
                        ft.Text("Don't have an account?", color=TEXT_MUTED, size=13),
                        ft.TextButton(
                            content=ft.Text("Sign up", color=ORANGE, size=13,
                                            weight=ft.FontWeight.BOLD),
                            on_click=go_register,
                            style=ft.ButtonStyle(
                                padding=ft.Padding(left=4, right=0, top=0, bottom=0),
                                overlay_color=ft.Colors.TRANSPARENT,
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                ),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    return ft.View(
        route="/login",
        bgcolor=BG,
        padding=0,
        controls=[
            ft.Container(
                expand=True,
                bgcolor=BG,
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                    controls=[
                        header,
                        ft.Container(height=28),
                        card,
                        ft.Container(height=24),
                    ],
                ),
            )
        ],
    )