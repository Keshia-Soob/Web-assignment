import flet as ft

# ── Colour palette (matches login screen exactly) ─────────────
ORANGE     = "#E65100"
BG         = "#FFFFFF"
CARD_BG    = "#F7F7F7"
SURFACE    = "#EFEFEF"
TEXT_DARK  = "#1A1A1A"
TEXT_MUTED = "#757575"
ERROR_RED  = "#EF5350"


def RegisterScreen(page, api, auth, go_menu):

    # ── Fields ────────────────────────────────────────────────
    def _field(label, hint, icon, keyboard=ft.KeyboardType.TEXT,
               password=False):
        return ft.TextField(
            label=label,
            hint_text=hint,
            keyboard_type=keyboard,
            prefix_icon=icon,
            password=password,
            can_reveal_password=password,
            border_radius=12,
            filled=True,
            fill_color=SURFACE,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            hint_style=ft.TextStyle(color=TEXT_MUTED),
            color=TEXT_DARK,
            border_color=SURFACE,
            focused_border_color=ORANGE,
            cursor_color=ORANGE,
            on_submit=lambda e: do_register(e),
        )

    first_name = _field("First name",  "Jane",               ft.Icons.PERSON_OUTLINE)
    last_name  = _field("Last name",   "Doe",                ft.Icons.PERSON_OUTLINE)
    email      = _field("Email",       "you@example.com",    ft.Icons.EMAIL_OUTLINED,
                        keyboard=ft.KeyboardType.EMAIL)
    phone      = _field("Phone",       "+230 5000 0000",     ft.Icons.PHONE_OUTLINED,
                        keyboard=ft.KeyboardType.PHONE)
    phone.value = "+230 "
    address    = _field("Address",     "12 Rue de la Paix",  ft.Icons.HOME_OUTLINED)
    password   = _field("Password",    "Min 8 characters",   ft.Icons.LOCK_OUTLINE,
                        password=True)

    status  = ft.Text(value="", color=ERROR_RED, size=13,
                      visible=False, text_align=ft.TextAlign.CENTER)
    loading = ft.ProgressRing(width=22, height=22, stroke_width=3,
                               color=ORANGE, visible=False)

    register_btn = ft.Button(
        content=ft.Text("Create Account", size=15,
                        weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        style=ft.ButtonStyle(
            bgcolor=ORANGE,
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding(left=0, right=0, top=14, bottom=14),
            overlay_color=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        ),
        width=305,
        on_click=lambda e: do_register(e),
    )

    # ── Handlers ──────────────────────────────────────────────
    def _set_loading(on: bool):
        register_btn.disabled = on
        loading.visible       = on
        status.visible        = False
        page.update()

    def _show_error(msg: str):
        status.value   = msg
        status.visible = True
        page.update()

    def _clear_errors():
        for f in [first_name, last_name, email, phone, address, password]:
            f.error_text = None

    def do_register(e):
        _clear_errors()
        status.visible = False

        # Required field validation
        required = {
            "First name is required": first_name,
            "Last name is required":  last_name,
            "Email is required":      email,
            "Password is required":   password,
        }
        has_error = False
        for msg, field in required.items():
            if not field.value or not field.value.strip():
                field.error_text = msg
                has_error = True

        if has_error:
            page.update()
            return

        if len(password.value) < 8:
            password.error_text = "Password must be at least 8 characters"
            page.update()
            return

        _set_loading(True)

        payload = {
            "first_name": first_name.value.strip(),
            "last_name":  last_name.value.strip(),
            "email":      email.value.strip(),
            "phone":      phone.value.strip(),
            "address":    address.value.strip(),
            "password":   password.value,
        }

        data, code = api._post("/auth/register/", payload)
        _set_loading(False)

        if code in [200, 201]:
            api.token = data.get("token")
            auth.save_token(api.token, email.value.strip())
            go_menu()
        else:
            _show_error(data.get("error", "Registration failed. Please try again."))

    def go_login(e):
        page.go("/login")

    # ── Branding header ───────────────────────────────────────
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
            ft.Text("Create your account", size=13, color=TEXT_MUTED),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=2,
    )

    # ── Card ──────────────────────────────────────────────────
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
                ft.Text("Join us today", size=20,
                        weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text("Fill in your details below", size=13, color=TEXT_MUTED),
                ft.Container(height=20),

                # First + Last name side by side
                ft.Row(
                    [
                        ft.Container(first_name, expand=1),
                        ft.Container(last_name,  expand=1),
                    ],
                    spacing=10,
                ),
                ft.Container(height=10),
                email,
                ft.Container(height=10),
                phone,
                ft.Container(height=10),
                address,
                ft.Container(height=10),
                password,
                ft.Container(height=6),

                status,
                ft.Container(height=6),

                ft.Row([register_btn, loading],
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

                # Login link
                ft.Row(
                    [
                        ft.Text("Already have an account?", color=TEXT_MUTED, size=13),
                        ft.TextButton(
                            content=ft.Text("Log in", color=ORANGE, size=13,
                                            weight=ft.FontWeight.BOLD),
                            on_click=go_login,
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
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    # ── Full screen view ──────────────────────────────────────
    return ft.View(
        route="/register",
        bgcolor=BG,
        padding=0,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Container(
                expand=True,
                bgcolor=BG,
                alignment=ft.Alignment(0, 0),
                padding=ft.Padding(left=0, right=0, top=32, bottom=32),
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