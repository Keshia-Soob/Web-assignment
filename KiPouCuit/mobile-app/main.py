"""
KiPouCuit Mobile App  —  main.py
=================================
A Flet mobile app that mirrors the KiPouCuit website features via the REST API.

BEFORE RUNNING:
  1. Start the Django server first:
       cd .../Web-assignment/KiPouCuit
       python manage.py runserver

  2. Then in a second terminal run this app:
       cd .../mobile_app
       flet run main.py

The two must run at the same time.
"""

import threading
import requests
import flet as ft

# ─── Change this if Django is running on a different port ───────────────────
BASE_URL = "http://127.0.0.1:8000/api"

CUISINE_EMOJI = {
    "mauritian": "🌴",
    "indian":    "🍛",
    "french":    "🥐",
    "english":   "🫖",
    "asian":     "🥢",
}

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

ORANGE = ft.Colors.ORANGE_700


# ─────────────────────────────────────────────────────────────────────────────
#  GPS  (desktop default = Port Louis, Mauritius)
#  On a real Android/iOS build this would call ft.Geolocator
# ─────────────────────────────────────────────────────────────────────────────

def _get_gps():
    return -20.1609, 57.4991   # Port Louis, Mauritius


# ─────────────────────────────────────────────────────────────────────────────
#  API CLIENT  — thin wrapper around every REST endpoint
# ─────────────────────────────────────────────────────────────────────────────

class ApiClient:
    def __init__(self):
        self.token       = None
        self.username    = None
        self.is_homecook = False

    def _h(self):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Token {self.token}"
        return h

    def _get(self, path, params=None):
        try:
            r = requests.get(f"{BASE_URL}{path}", params=params,
                             headers=self._h(), timeout=8)
            return r.json(), r.status_code
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot reach the server.\n\n"
                             "Make sure Django is running:\n"
                             "  python manage.py runserver"}, 0
        except Exception as e:
            return {"error": str(e)}, 0

    def _post(self, path, data=None):
        try:
            r = requests.post(f"{BASE_URL}{path}", json=data or {},
                              headers=self._h(), timeout=8)
            return r.json(), r.status_code
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot reach the server.\n\n"
                             "Make sure Django is running:\n"
                             "  python manage.py runserver"}, 0
        except Exception as e:
            return {"error": str(e)}, 0

    # Auth
    def login(self, username, password):
        data, code = self._post("/auth/login/",
                                {"username": username, "password": password})
        if code == 200:
            self.token       = data["token"]
            self.username    = data["username"]
            self.is_homecook = data.get("is_homecook", False)
        return data, code

    def logout(self):
        self._post("/auth/logout/")
        self.token = self.username = None
        self.is_homecook = False

    # Menu
    def get_menu(self, cuisine=None, search=None):
        p = {}
        if cuisine: p["cuisine"] = cuisine
        if search:  p["search"]  = search
        return self._get("/menu/", p)

    def get_nearby_menu(self, lat, lng, radius_km=10):
        return self._get("/menu/nearby/",
                         {"lat": lat, "lng": lng, "radius_km": radius_km})

    # Cart
    def get_cart(self):          return self._get("/cart/")
    def add_to_cart(self, iid):  return self._post("/cart/add/",    {"item_id": iid})
    def remove_from_cart(self, iid): return self._post("/cart/remove/", {"item_id": iid})

    # Orders
    def place_order(self, name, lat=None, lng=None):
        return self._post("/orders/place/",
                          {"client_name": name,
                           "delivery_lat": lat, "delivery_lng": lng})
    def get_orders(self):        return self._get("/orders/")

    # Reviews
    def get_reviews(self):       return self._get("/reviews/")
    def post_review(self, rating, message):
        return self._post("/reviews/create/",
                          {"rating": rating, "message": message})

    # Location sensor endpoint
    def send_location(self, lat, lng, role="customer"):
        return self._post("/location/update/",
                          {"lat": lat, "lng": lng, "role": role})

    # HomeCook dashboard
    def get_homecook_items(self):   return self._get("/homecook/items/")
    def accept_item(self, item_id): return self._post(f"/homecook/accept/{item_id}/")
    def mark_ready(self, item_id):  return self._post(f"/homecook/ready/{item_id}/")
    def mark_delivered(self, item_id): return self._post(f"/homecook/delivered/{item_id}/")


api = ApiClient()


# ─────────────────────────────────────────────────────────────────────────────
#  SHARED WIDGETS
# ─────────────────────────────────────────────────────────────────────────────

def app_bar(title):
    return ft.AppBar(
        title=ft.Text(title, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor=ORANGE,
        center_title=True,
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
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        margin=ft.margin.symmetric(horizontal=8, vertical=4),
    )


def bottom_nav(selected, page):
    routes = ["/menu", "/nearby", "/cart", "/orders", "/reviews"]
    destinations = [
        ft.NavigationBarDestination(icon=ft.Icons.RESTAURANT_MENU, label="Menu"),
        ft.NavigationBarDestination(icon=ft.Icons.LOCATION_ON,     label="Nearby"),
        ft.NavigationBarDestination(icon=ft.Icons.SHOPPING_CART,   label="Cart"),
        ft.NavigationBarDestination(icon=ft.Icons.RECEIPT_LONG,    label="Orders"),
        ft.NavigationBarDestination(icon=ft.Icons.STAR_BORDER,     label="Reviews"),
    ]
    if api.is_homecook:
        routes.append("/cook")
        destinations.append(
            ft.NavigationBarDestination(icon=ft.Icons.SOUP_KITCHEN, label="Cook")
        )
    return ft.NavigationBar(
        destinations=destinations,
        selected_index=selected,
        bgcolor=ft.Colors.WHITE,
        on_change=lambda e: page.go(routes[e.control.selected_index]),
    )


def item_card(item, on_add):
    """Menu item card — mirrors the website's menu grid."""
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
                        style=ft.ButtonStyle(bgcolor=ORANGE,
                                             color=ft.Colors.WHITE),
                        height=34,
                        on_click=lambda e, i=item: on_add(i),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=6),
            padding=ft.padding.symmetric(horizontal=14, vertical=12),
        ),
        elevation=2,
        margin=ft.margin.symmetric(vertical=4, horizontal=8),
    )


# ─────────────────────────────────────────────────────────────────────────────
#  SCREEN: LOGIN
#  Mirrors: /login on the website
# ─────────────────────────────────────────────────────────────────────────────

def login_view(page):
    username_f = ft.TextField(label="Username", prefix_icon=ft.Icons.PERSON,
                               autofocus=True)
    password_f = ft.TextField(label="Password", prefix_icon=ft.Icons.LOCK,
                               password=True, can_reveal_password=True)
    status_t   = ft.Text("", color=ft.Colors.RED_600, size=13)
    loading    = ft.ProgressBar(visible=False)

    def do_login(e):
        if not username_f.value.strip() or not password_f.value.strip():
            status_t.value = "Please enter username and password."
            page.update()
            return
        loading.visible = True
        status_t.value  = ""
        page.update()
        data, code = api.login(username_f.value.strip(),
                               password_f.value.strip())
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
                    ft.Text("Welcome to KiPouCuit", size=22,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text("Home-cooked Mauritian food\ndelivered to your door",
                            color=ft.Colors.GREY_600, size=13,
                            text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=20),
                    username_f,
                    password_f,
                    status_t,
                    loading,
                    ft.ElevatedButton(
                        "Login",
                        icon=ft.Icons.LOGIN,
                        style=ft.ButtonStyle(bgcolor=ORANGE,
                                             color=ft.Colors.WHITE),
                        width=280,
                        on_click=do_login,
                    ),
                    ft.Text(
                        "Don't have an account? Register on the website first.",
                        color=ft.Colors.GREY_500, size=11,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   spacing=12),
                padding=30,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  SCREEN: MENU
#  Mirrors: /menu on the website — browse, filter by cuisine, add to cart
# ─────────────────────────────────────────────────────────────────────────────

def menu_view(page, snack):
    content    = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
    search_f   = ft.TextField(hint_text="Search dishes…",
                               prefix_icon=ft.Icons.SEARCH,
                               border_radius=30, expand=True)
    cuisine_dd = ft.Dropdown(
        hint_text="All Cuisines",
        options=[ft.dropdown.Option(key="", text="All Cuisines")] + [
            ft.dropdown.Option(key=k, text=f"{v}  {k.capitalize()}")
            for k, v in CUISINE_EMOJI.items()
        ],
        width=160,
    )

    def add_to_cart(item):
        if not api.token:
            snack("⚠️  Please login first to add items to cart")
            return
        _, code = api.add_to_cart(item["id"])
        snack(f"✅  {item['name']} added to cart" if code == 200
              else "❌  Could not add item — is the server running?")

    def load(e=None):
        content.controls.clear()
        content.controls.append(spinner())
        page.update()
        items, code = api.get_menu(
            cuisine=cuisine_dd.value or None,
            search=search_f.value.strip() or None,
        )
        content.controls.clear()
        if code == 0:
            content.controls.append(err_banner(items.get("error", "Server error")))
        elif code != 200 or not isinstance(items, list):
            content.controls.append(err_banner("Could not load menu."))
        elif not items:
            content.controls.append(
                ft.Text("No items found.", color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER))
        else:
            for itm in items:
                content.controls.append(item_card(itm, add_to_cart))
        page.update()

    search_f.on_submit   = load
    cuisine_dd.on_change = load
    threading.Thread(target=load, daemon=True).start()

    return ft.View(
        route="/menu",
        appbar=app_bar("Menu"),
        navigation_bar=bottom_nav(0, page),
        controls=[
            ft.Container(
                ft.Row([search_f, cuisine_dd]),
                padding=ft.padding.symmetric(horizontal=10, vertical=8),
            ),
            ft.Container(content, expand=True,
                         padding=ft.padding.only(bottom=10)),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
#  SCREEN: NEARBY  ← GPS SENSOR
#  Uses device GPS to send lat/lng to /api/menu/nearby/
#  This is the feature that differentiates mobile from web
# ─────────────────────────────────────────────────────────────────────────────

def nearby_view(page, snack):
    content  = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
    loc_text = ft.Text("Tap below to find meals near your location",
                       color=ft.Colors.GREY_600, size=13,
                       text_align=ft.TextAlign.CENTER)

    def add_to_cart(item):
        if not api.token:
            snack("⚠️  Please login first")
            return
        _, code = api.add_to_cart(item["id"])
        snack(f"✅  {item['name']} added" if code == 200 else "❌  Error adding item")

    def load(e=None):
        loc_text.value = "🔄  Detecting your GPS location…"
        page.update()

        # ── GPS SENSOR ──────────────────────────────────────────────────────
        # _get_gps() returns the device coordinates.
        # On desktop this is the Port Louis default.
        # On Android/iOS this would use the real GPS hardware.
        lat, lng = _get_gps()

        loc_text.value = f"📍  Your location: {lat:.5f}, {lng:.5f}"

        # Push our location to the server (sensor data endpoint)
        api.send_location(lat, lng, role="customer")

        content.controls.clear()
        content.controls.append(
            ft.Text("Finding meals near you…",
                    color=ft.Colors.GREY_500, size=12))
        page.update()

        data, code = api.get_nearby_menu(lat, lng)
        content.controls.clear()

        if code == 0:
            content.controls.append(err_banner(data.get("error", "Server error")))
        elif code != 200:
            content.controls.append(err_banner("Could not fetch nearby meals."))
        else:
            items = data.get("items", [])
            if not items:
                content.controls.append(
                    ft.Text("No meals found nearby.",
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER))
            else:
                content.controls.append(
                    ft.Text(f"Found {len(items)} meals near you",
                            color=ft.Colors.GREEN_700,
                            weight=ft.FontWeight.BOLD,
                            size=13))
                for itm in items:
                    content.controls.append(item_card(itm, add_to_cart))
        page.update()

    return ft.View(
        route="/nearby",
        appbar=app_bar("📍  Nearby Meals"),
        navigation_bar=bottom_nav(1, page),
        controls=[
            ft.Container(
                ft.Column([
                    ft.Icon(ft.Icons.LOCATION_ON, size=40, color=ORANGE),
                    loc_text,
                    ft.ElevatedButton(
                        "Find Meals Near Me",
                        icon=ft.Icons.GPS_FIXED,
                        style=ft.ButtonStyle(
                            bgcolor=ORANGE, color=ft.Colors.WHITE),
                        width=250,
                        on_click=lambda e: threading.Thread(
                            target=load, daemon=True).start(),
                    ),
                    ft.Text(
                        "📱  On a real device this uses your GPS.\n"
                        "     On desktop it defaults to Port Louis.",
                        color=ft.Colors.GREY_400, size=11,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   spacing=10),
                padding=16,
            ),
            ft.Container(content, expand=True),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
#  SCREEN: CART / ORDER SUMMARY
#  Mirrors: /order-summary + /checkout on the website
# ─────────────────────────────────────────────────────────────────────────────

def cart_view(page, snack):
    content      = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    total_text   = ft.Text("Total: Rs 0.00", size=17,
                            weight=ft.FontWeight.BOLD)
    checkout_btn = ft.ElevatedButton(
        "Place Order",
        icon=ft.Icons.CHECK_CIRCLE,
        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700,
                             color=ft.Colors.WHITE),
        width=280,
        disabled=True,
    )

    def remove(item_id, name):
        api.remove_from_cart(item_id)
        snack(f"Removed {name} from cart")
        threading.Thread(target=load_cart, daemon=True).start()

    def load_cart():
        content.controls.clear()
        content.controls.append(spinner())
        page.update()
        data, code = api.get_cart()
        content.controls.clear()
        if code == 0:
            content.controls.append(err_banner(data.get("error", "")))
            page.update()
            return
        if code != 200:
            content.controls.append(err_banner("Could not load cart."))
            page.update()
            return

        items    = data.get("items", [])
        subtotal = data.get("subtotal", 0.0)

        if not items:
            content.controls.append(
                ft.Column([
                    ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED,
                            size=60, color=ft.Colors.GREY_300),
                    ft.Text("Your cart is empty",
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER),
                    ft.TextButton("Browse Menu →",
                                  on_click=lambda e: page.go("/menu")),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   spacing=8)
            )
            checkout_btn.disabled = True
        else:
            checkout_btn.disabled = False
            for ci in items:
                content.controls.append(
                    ft.ListTile(
                        leading=ft.Text(
                            CUISINE_EMOJI.get(ci.get("cuisine",""), "🍽️"),
                            size=22),
                        title=ft.Text(ci["name"],
                                      weight=ft.FontWeight.W_600),
                        subtitle=ft.Text(
                            f"Qty: {ci['quantity']}   ·   "
                            f"Rs {ci['line_total']:.0f}"),
                        trailing=ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.RED_400,
                            tooltip="Remove",
                            on_click=lambda e, iid=ci["item_id"],
                            n=ci["name"]: remove(iid, n),
                        ),
                    )
                )
            content.controls.append(ft.Divider())

        total_text.value = f"Total: Rs {subtotal:.2f}"
        page.update()

    def place_order(e):
        if not api.token:
            snack("⚠️  Please login first")
            return
        # ── GPS SENSOR: attach delivery coordinates to the order ────────────
        # The server stores these so the cook knows where to deliver.
        lat, lng = _get_gps()
        data, code = api.place_order(
            name=api.username or "Guest",
            lat=lat, lng=lng,
        )
        if code == 201:
            snack(f"✅  Order #{data['order_id']} placed!")
            threading.Thread(target=load_cart, daemon=True).start()
            page.go("/orders")
        elif code == 0:
            snack(f"❌  {data.get('error', 'Server not reachable')}")
        else:
            snack(f"❌  {data.get('error', 'Could not place order')}")

    checkout_btn.on_click = place_order
    threading.Thread(target=load_cart, daemon=True).start()

    return ft.View(
        route="/cart",
        appbar=app_bar("🛒  Cart"),
        navigation_bar=bottom_nav(2, page),
        controls=[
            ft.Container(content, expand=True, padding=8),
            ft.Container(
                ft.Column([
                    total_text,
                    checkout_btn,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   spacing=8),
                padding=16,
            ),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
#  SCREEN: ORDERS  — live status tracking
#  Mirrors: /order-summary (status view) on the website
# ─────────────────────────────────────────────────────────────────────────────

def orders_view(page):
    content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def load_orders():
        content.controls.clear()
        if not api.token:
            content.controls.append(
                ft.Column([
                    ft.Icon(ft.Icons.LOCK_OUTLINE,
                            size=50, color=ft.Colors.GREY_300),
                    ft.Text("Login to view your orders",
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER),
                    ft.TextButton("Go to Login →",
                                  on_click=lambda e: page.go("/login")),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   spacing=8))
            page.update()
            return

        content.controls.append(spinner())
        page.update()
        orders, code = api.get_orders()
        content.controls.clear()

        if code == 0:
            content.controls.append(err_banner(orders.get("error", "")))
            page.update()
            return
        if code != 200 or not isinstance(orders, list):
            content.controls.append(err_banner("Could not load orders."))
            page.update()
            return

        if not orders:
            content.controls.append(
                ft.Column([
                    ft.Icon(ft.Icons.RECEIPT_LONG,
                            size=50, color=ft.Colors.GREY_300),
                    ft.Text("No orders yet",
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER),
                    ft.TextButton("Browse Menu →",
                                  on_click=lambda e: page.go("/menu")),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   spacing=8))
        else:
            for order in orders:
                st    = order["status"]
                color = STATUS_COLOR.get(st, ft.Colors.GREY_400)
                icon  = STATUS_ICON.get(st, ft.Icons.INFO_OUTLINE)
                item_rows = [
                    ft.Text(f"  • {it['name']}  ×{it['quantity']}   "
                            f"Rs {float(it['price'])*it['quantity']:.0f}",
                            size=12)
                    for it in order["items"]
                ]
                content.controls.append(
                    ft.Card(
                        content=ft.Container(
                            ft.Column([
                                ft.Row([
                                    ft.Icon(icon, color=color, size=20),
                                    ft.Text(f"Order #{order['id']}",
                                            weight=ft.FontWeight.BOLD,
                                            expand=True),
                                    ft.Container(
                                        ft.Text(order["human_status"],
                                                color=ft.Colors.WHITE,
                                                size=11,
                                                weight=ft.FontWeight.W_600),
                                        bgcolor=color,
                                        border_radius=12,
                                        padding=ft.padding.symmetric(
                                            horizontal=8, vertical=3),
                                    ),
                                ]),
                                ft.Text(
                                    f"Rs {order['subtotal']:.2f}   ·   "
                                    f"{order['created_at'][:10]}",
                                    size=12, color=ft.Colors.GREY_600),
                                ft.Divider(height=6),
                                *item_rows,
                            ], spacing=5),
                            padding=14,
                        ),
                        elevation=2,
                        margin=ft.margin.symmetric(vertical=4, horizontal=8),
                    )
                )
        page.update()

    threading.Thread(target=load_orders, daemon=True).start()

    return ft.View(
        route="/orders",
        appbar=app_bar("📦  My Orders"),
        navigation_bar=bottom_nav(3, page),
        controls=[
            ft.Container(
                ft.ElevatedButton(
                    "Refresh",
                    icon=ft.Icons.REFRESH,
                    on_click=lambda e: threading.Thread(
                        target=load_orders, daemon=True).start(),
                ),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
            ),
            ft.Container(content, expand=True),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
#  SCREEN: REVIEWS
#  Mirrors: /reviews on the website
# ─────────────────────────────────────────────────────────────────────────────

def reviews_view(page, snack):
    list_col  = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    rating_sl = ft.Slider(min=1, max=5, divisions=4, value=5,
                          label="{value} ⭐", active_color=ORANGE)
    message_f = ft.TextField(label="Write your review",
                              multiline=True, min_lines=3, max_lines=5)
    submit_st = ft.Text("", color=ft.Colors.GREEN_700, size=13)

    def load_reviews():
        list_col.controls.clear()
        list_col.controls.append(spinner())
        page.update()
        reviews, code = api.get_reviews()
        list_col.controls.clear()
        if code == 0:
            list_col.controls.append(
                err_banner(reviews.get("error", "Server error")))
        elif code != 200 or not isinstance(reviews, list):
            list_col.controls.append(err_banner("Could not load reviews."))
        else:
            for r in reviews[:20]:
                stars = "⭐" * int(r["rating"])
                list_col.controls.append(
                    ft.Card(
                        content=ft.Container(
                            ft.Column([
                                ft.Row([
                                    ft.Text(
                                        f"{r['first_name']} {r['last_name']}",
                                        weight=ft.FontWeight.BOLD,
                                        expand=True),
                                    ft.Text(stars, size=14),
                                ]),
                                ft.Text(r["message"], size=13,
                                        color=ft.Colors.GREY_700),
                                ft.Text(r["created_at"][:10],
                                        size=11, color=ft.Colors.GREY_400),
                            ], spacing=4),
                            padding=12,
                        ),
                        elevation=2,
                        margin=ft.margin.symmetric(vertical=4, horizontal=8),
                    )
                )
        page.update()

    def submit_review(e):
        if not api.token:
            snack("⚠️  Please login first")
            return
        if not message_f.value.strip():
            snack("Please write a review message")
            return
        data, code = api.post_review(
            rating=int(rating_sl.value),
            message=message_f.value.strip(),
        )
        if code == 201:
            submit_st.value = "✅  Review posted!"
            message_f.value = ""
        elif code == 403:
            submit_st.value = "⚠️  You need a delivered order before reviewing."
        elif code == 0:
            submit_st.value = f"❌  {data.get('error', 'Server not reachable')}"
        else:
            submit_st.value = f"❌  {data.get('error', 'Could not post review')}"
        page.update()
        threading.Thread(target=load_reviews, daemon=True).start()

    threading.Thread(target=load_reviews, daemon=True).start()

    return ft.View(
        route="/reviews",
        appbar=app_bar("⭐  Reviews"),
        navigation_bar=bottom_nav(4, page),
        controls=[
            ft.Container(
                ft.Column([
                    ft.Text("Leave a Review",
                            weight=ft.FontWeight.BOLD, size=16),
                    ft.Text("Rating:", size=13, color=ft.Colors.GREY_600),
                    rating_sl,
                    message_f,
                    submit_st,
                    ft.ElevatedButton(
                        "Submit Review",
                        icon=ft.Icons.STAR,
                        style=ft.ButtonStyle(bgcolor=ORANGE,
                                             color=ft.Colors.WHITE),
                        on_click=submit_review,
                    ),
                ], spacing=8),
                padding=14,
            ),
            ft.Divider(),
            ft.Container(
                ft.Text("Customer Reviews",
                        weight=ft.FontWeight.BOLD, size=15),
                padding=ft.padding.symmetric(horizontal=12, vertical=4),
            ),
            ft.Container(list_col, expand=True),
        ],
        scroll=ft.ScrollMode.AUTO,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  SCREEN: HOMECOOK DASHBOARD  ← GPS SENSOR (cook shares live location)
#  Mirrors: /homecook-log on the website
#  Only shown if the logged-in user is a HomeCook
# ─────────────────────────────────────────────────────────────────────────────

def cook_view(page, snack):
    avail_col = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    mine_col  = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    loc_text  = ft.Text("", color=ft.Colors.GREY_500, size=12)

    def share_location(e=None):
        # ── GPS SENSOR: cook shares position when delivering ────────────────
        lat, lng = _get_gps()
        api.send_location(lat, lng, role="cook")
        loc_text.value = f"📍  Location shared: {lat:.5f}, {lng:.5f}"
        page.update()

    def action_btn(label, color, on_click):
        return ft.ElevatedButton(
            label,
            style=ft.ButtonStyle(bgcolor=color, color=ft.Colors.WHITE),
            height=32,
            on_click=on_click,
        )

    def load(e=None):
        avail_col.controls.clear()
        mine_col.controls.clear()
        avail_col.controls.append(spinner())
        mine_col.controls.append(spinner())
        page.update()

        data, code = api.get_homecook_items()
        avail_col.controls.clear()
        mine_col.controls.clear()

        if code == 0:
            avail_col.controls.append(err_banner(data.get("error", "")))
            page.update()
            return
        if code != 200:
            avail_col.controls.append(err_banner("Could not load orders."))
            page.update()
            return

        available = data.get("available", [])
        my_items  = data.get("my_items", [])

        if not available:
            avail_col.controls.append(
                ft.Text("No pending orders for your cuisine.",
                        color=ft.Colors.GREY_500, size=13))
        for it in available:
            avail_col.controls.append(
                ft.Card(
                    content=ft.Container(
                        ft.Column([
                            ft.Text(it["name"], weight=ft.FontWeight.BOLD),
                            ft.Text(f"Qty: {it['quantity']}   ·   "
                                    f"Order #{it['order_id']}", size=12,
                                    color=ft.Colors.GREY_600),
                            action_btn(
                                "Accept",
                                ft.Colors.BLUE_600,
                                lambda e, iid=it["id"]: _do(
                                    api.accept_item, iid, load, snack,
                                    "Accepted!", page),
                            ),
                        ], spacing=6),
                        padding=12,
                    ),
                    elevation=2,
                    margin=ft.margin.symmetric(vertical=4, horizontal=8),
                )
            )

        if not my_items:
            mine_col.controls.append(
                ft.Text("No active items assigned to you.",
                        color=ft.Colors.GREY_500, size=13))
        for it in my_items:
            st = it["status"]
            btns = []
            if st == "accepted":
                btns.append(action_btn(
                    "Mark Delivering", ft.Colors.PURPLE_600,
                    lambda e, iid=it["id"]: _do(
                        api.mark_ready, iid, load, snack,
                        "Marked as delivering!", page),
                ))
            elif st == "delivering":
                btns.append(action_btn(
                    "Mark Delivered ✓", ft.Colors.GREEN_700,
                    lambda e, iid=it["id"]: _do(
                        api.mark_delivered, iid, load, snack,
                        "Delivered! ✅", page),
                ))
                btns.append(
                    ft.ElevatedButton(
                        "📍 Share My Location",
                        style=ft.ButtonStyle(
                            bgcolor=ORANGE, color=ft.Colors.WHITE),
                        height=32,
                        on_click=share_location,
                    )
                )
            mine_col.controls.append(
                ft.Card(
                    content=ft.Container(
                        ft.Column([
                            ft.Row([
                                ft.Text(it["name"],
                                        weight=ft.FontWeight.BOLD,
                                        expand=True),
                                ft.Container(
                                    ft.Text(st.capitalize(),
                                            color=ft.Colors.WHITE,
                                            size=11),
                                    bgcolor=STATUS_COLOR.get(
                                        st, ft.Colors.GREY_400),
                                    border_radius=10,
                                    padding=ft.padding.symmetric(
                                        horizontal=7, vertical=3),
                                ),
                            ]),
                            ft.Text(f"Order #{it['order_id']}",
                                    size=12, color=ft.Colors.GREY_600),
                            *btns,
                        ], spacing=6),
                        padding=12,
                    ),
                    elevation=2,
                    margin=ft.margin.symmetric(vertical=4, horizontal=8),
                )
            )

        page.update()

    threading.Thread(target=load, daemon=True).start()

    return ft.View(
        route="/cook",
        appbar=app_bar("👨‍🍳  Cook Dashboard"),
        navigation_bar=bottom_nav(5, page),
        controls=[
            ft.Container(
                ft.Row([
                    ft.ElevatedButton(
                        "Refresh",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e: threading.Thread(
                            target=load, daemon=True).start(),
                    ),
                    loc_text,
                ], spacing=10),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
            ),
            ft.Container(
                ft.Text("🆕  Available Orders",
                        weight=ft.FontWeight.BOLD, size=14),
                padding=ft.padding.symmetric(horizontal=12, vertical=4),
            ),
            ft.Container(avail_col, expand=True),
            ft.Divider(),
            ft.Container(
                ft.Text("📋  My Active Orders",
                        weight=ft.FontWeight.BOLD, size=14),
                padding=ft.padding.symmetric(horizontal=12, vertical=4),
            ),
            ft.Container(mine_col, expand=True),
        ],
        scroll=ft.ScrollMode.AUTO,
    )


def _do(fn, item_id, reload, snack, success_msg, page):
    """Helper: call an API action, show result, reload."""
    data, code = fn(item_id)
    if code in (200, 201):
        snack(success_msg)
    else:
        snack(f"❌  {data.get('error', 'Action failed')}")
    threading.Thread(target=reload, daemon=True).start()


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main(page: ft.Page):
    page.title        = "KiPouCuit"
    page.theme_mode   = ft.ThemeMode.LIGHT
    page.theme        = ft.Theme(color_scheme_seed=ft.Colors.ORANGE)
    page.padding      = 0
    page.window.width  = 390
    page.window.height = 844

    def snack(msg):
        page.snack_bar      = ft.SnackBar(ft.Text(msg),
                                          bgcolor=ft.Colors.GREY_800)
        page.snack_bar.open = True
        page.update()

    def route_change(e):
        page.views.clear()
        r = page.route
        if   r == "/login":   page.views.append(login_view(page))
        elif r == "/menu":    page.views.append(menu_view(page, snack))
        elif r == "/nearby":  page.views.append(nearby_view(page, snack))
        elif r == "/cart":    page.views.append(cart_view(page, snack))
        elif r == "/orders":  page.views.append(orders_view(page))
        elif r == "/reviews": page.views.append(reviews_view(page, snack))
        elif r == "/cook":    page.views.append(cook_view(page, snack))
        else:
            page.go("/login")
            return
        page.update()

    def view_pop(e):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop     = view_pop
    page.go("/login" if not api.token else "/menu")


if __name__ == "__main__":
    ft.app(target=main)