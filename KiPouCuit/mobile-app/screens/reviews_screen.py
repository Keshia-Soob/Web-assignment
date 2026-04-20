"""
screens/reviews_screen.py
─────────────────────────
KiPouCuit mobile app – Reviews screen.

Mirrors the Django web app logic exactly:
  • GET  /api/reviews/         → list all reviews (public)
  • POST /api/reviews/create/  → submit a review (auth + ≥1 delivered order)

Review model fields: first_name, last_name, rating, message, created_at
The API auto-fills first_name / last_name / email from the logged-in user.
"""

import threading
import flet as ft

from components.shared import app_bar, spinner, err_banner, bottom_nav, ORANGE


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def _star_display(rating: int) -> str:
    """Return filled + empty stars as a unicode string."""
    return "★" * rating + "☆" * (5 - rating)


def _review_card(review: dict) -> ft.Card:
    """Read-only card for a single review – mirrors review_list.html."""
    full_name = f"{review.get('first_name', '')} {review.get('last_name', '')}".strip()
    rating = review.get("rating", 0)
    message = review.get("message", "")
    created_at = review.get("created_at", "")[:10]  # YYYY-MM-DD

    return ft.Card(
        elevation=2,
        margin=ft.margin.symmetric(vertical=5, horizontal=8),
        content=ft.Container(
            padding=ft.padding.symmetric(horizontal=14, vertical=12),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                full_name,
                                weight=ft.FontWeight.BOLD,
                                size=14,
                                expand=True,
                            ),
                            ft.Text(
                                created_at,
                                size=11,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                    ),
                    ft.Text(
                        _star_display(rating),
                        size=16,
                        color=ft.Colors.AMBER_600,
                    ),
                    ft.Text(
                        message,
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
            ),
        ),
    )


# ─────────────────────────────────────────────
#  MAIN VIEW FACTORY
# ─────────────────────────────────────────────

def create_reviews_view(page: ft.Page, api, show_snack) -> ft.View:
    """
    Build and return the ft.View for /reviews.
    Call  page.views.append(create_reviews_view(...))  from the router.
    """

    # ── shared state ────────────────────────────────────────────
    selected_rating = [0]          # mutable container so closures can write
    star_buttons: list[ft.IconButton] = []
    is_loading = [False]

    # ── refs to mutable controls ────────────────────────────────
    message_field = ft.TextField(
        label="Your message",
        multiline=True,
        min_lines=3,
        max_lines=6,
        border_radius=10,
        filled=True,
        hint_text="Share your experience…",
    )

    form_feedback = ft.Text("", size=13)

    reviews_col = ft.Column(
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    loading_bar = ft.ProgressBar(visible=False)

    # ── star picker ──────────────────────────────────────────────
    def _on_star_click(e):
        selected_rating[0] = e.control.data
        _refresh_stars()
        page.update()

    def _refresh_stars():
        for btn in star_buttons:
            filled = btn.data <= selected_rating[0]
            btn.icon = ft.Icons.STAR if filled else ft.Icons.STAR_BORDER
            btn.icon_color = ft.Colors.AMBER_500 if filled else ft.Colors.GREY_400

    for i in range(1, 6):
        star_buttons.append(
            ft.IconButton(
                icon=ft.Icons.STAR_BORDER,
                icon_color=ft.Colors.GREY_400,
                icon_size=30,
                data=i,
                on_click=_on_star_click,
                tooltip=f"{i} star{'s' if i > 1 else ''}",
                style=ft.ButtonStyle(padding=ft.padding.all(2)),
            )
        )

    stars_row = ft.Row(star_buttons, spacing=0)

    # ── submit handler ───────────────────────────────────────────
    submit_btn = ft.ElevatedButton(
        "Post your Review",
        icon=ft.Icons.SEND_ROUNDED,
        style=ft.ButtonStyle(
            bgcolor=ORANGE,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )

    def _submit(e):
        if is_loading[0]:
            return

        # Client-side validation
        errors = []
        if selected_rating[0] == 0:
            errors.append("Please select a star rating.")
        if not message_field.value or not message_field.value.strip():
            errors.append("Message is required.")

        if errors:
            form_feedback.value = " | ".join(errors)
            form_feedback.color = ft.Colors.RED_600
            page.update()
            return

        # Disable UI
        is_loading[0] = True
        submit_btn.disabled = True
        loading_bar.visible = True
        form_feedback.value = ""
        page.update()

        def _do_post():
            data, code = api.post_review(
                rating=selected_rating[0],
                message=message_field.value.strip(),
            )

            is_loading[0] = False
            submit_btn.disabled = False
            loading_bar.visible = False

            if code == 201:
                # Reset form
                selected_rating[0] = 0
                _refresh_stars()
                message_field.value = ""
                form_feedback.value = "✅ Your review has been posted!"
                form_feedback.color = ft.Colors.GREEN_700
                _load_reviews()   # refresh the list
            elif code == 403:
                form_feedback.value = (
                    data.get("error")
                    or "⚠️ You need at least one delivered order to post a review."
                )
                form_feedback.color = ft.Colors.RED_600
                page.update()
            else:
                form_feedback.value = data.get("error", "Something went wrong.")
                form_feedback.color = ft.Colors.RED_600
                page.update()

        threading.Thread(target=_do_post, daemon=True).start()

    submit_btn.on_click = _submit

    # ── load reviews ─────────────────────────────────────────────
    def _load_reviews():
        loading_bar.visible = True
        reviews_col.controls.clear()
        page.update()

        data, code = api.get_reviews()

        loading_bar.visible = False

        if code != 200 or isinstance(data, dict) and "error" in data:
            reviews_col.controls.append(
                err_banner(data.get("error", "Could not load reviews."))
            )
        elif not data:
            reviews_col.controls.append(
                ft.Container(
                    padding=ft.padding.all(20),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.RATE_REVIEW_OUTLINED,
                                    size=48, color=ft.Colors.GREY_400),
                            ft.Text("No reviews yet – be the first!",
                                    color=ft.Colors.GREY_500),
                        ],
                    ),
                )
            )
        else:
            for rev in data:
                reviews_col.controls.append(_review_card(rev))

        page.update()

    # ── assemble form section ────────────────────────────────────
    if not api.token:
        form_section = ft.Container(
            padding=ft.padding.all(20),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.LOCK_OUTLINE,
                            size=40, color=ft.Colors.GREY_400),
                    ft.Text("Log in to leave a review.",
                            color=ft.Colors.GREY_500),
                ],
            ),
        )
    else:
        form_section = ft.Container(
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text("Write a Review",
                            size=16, weight=ft.FontWeight.W_600),
                    ft.Row(
                        controls=[
                            ft.Text("Rating:", size=14),
                            stars_row,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    message_field,
                    form_feedback,
                    submit_btn,
                ],
            ),
        )

    # ── full view ────────────────────────────────────────────────
    view = ft.View(
        route="/reviews",
        padding=0,
        appbar=app_bar("Reviews"),
        navigation_bar=bottom_nav(4, page),   # index 4 = Reviews tab
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    loading_bar,
                    # ── Post a Review form ──
                    form_section,
                    ft.Divider(height=1),
                    # ── All Reviews header ──
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=16, vertical=8),
                        content=ft.Text(
                            "All Reviews",
                            size=16,
                            weight=ft.FontWeight.W_600,
                        ),
                    ),
                    # ── Review list ──
                    reviews_col,
                ],
            )
        ],
    )

    # Kick off the initial load
    threading.Thread(target=_load_reviews, daemon=True).start()

    return view