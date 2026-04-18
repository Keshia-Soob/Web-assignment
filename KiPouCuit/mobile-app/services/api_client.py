# services/api_client.py

import requests

BASE_URL = "http://127.0.0.1:8000/api"


class ApiClient:
    def __init__(self):
        self.token = None
        self.username = None
        self.is_homecook = False

    def _h(self):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Token {self.token}"
        return h

    # SAFE GET
    def _get(self, path, params=None):
        try:
            r = requests.get(
                f"{BASE_URL}{path}",
                params=params,
                headers=self._h(),
                timeout=8
            )

            try:
                return r.json(), r.status_code
            except:
                return {"error": r.text}, r.status_code

        except Exception as e:
            return {"error": str(e)}, 0

    # SAFE POST
    def _post(self, path, data=None):
        try:
            r = requests.post(
                f"{BASE_URL}{path}",
                json=data or {},
                headers=self._h(),
                timeout=8
            )

            try:
                return r.json(), r.status_code
            except:
                return {"error": r.text}, r.status_code

        except Exception as e:
            return {"error": str(e)}, 0

    # AUTH
    def login(self, username, password):
        print("LOGIN REQUEST SENT")
        print("USERNAME:", username)
        print("PASSWORD:", password)

        data, code = self._post("/auth/login/", {
            "username": username,
            "password": password
        })

        print("RESPONSE:", data)
        print("STATUS:", code)

        if code == 200:
            self.token = data.get("token")
            self.username = data.get("username")

        return data, code

    def logout(self):
        self._post("/auth/logout/")
        self.token = None
        self.username = None
        self.is_homecook = False

    # MENU
    def get_menu(self, cuisine=None, search=None):
        p = {}
        if cuisine:
            p["cuisine"] = cuisine
        if search:
            p["search"] = search
        return self._get("/menu/", p)

    def get_nearby_menu(self, lat, lng, radius_km=10):
        return self._get("/menu/nearby/", {
            "lat": lat,
            "lng": lng,
            "radius_km": radius_km
        })

    # CART
    def get_cart(self):
        return self._get("/cart/")

    def add_to_cart(self, iid):
        return self._post("/cart/add/", {"item_id": iid})

    def remove_from_cart(self, iid):
        return self._post("/cart/remove/", {"item_id": iid})

    # ORDERS
    def place_order(self, name, lat=None, lng=None):
        return self._post("/orders/place/", {
            "client_name": name,
            "delivery_lat": lat,
            "delivery_lng": lng
        })

    def get_orders(self):
        return self._get("/orders/")

    # REVIEWS
    def get_reviews(self):
        return self._get("/reviews/")

    def post_review(self, rating, message):
        return self._post("/reviews/create/", {
            "rating": rating,
            "message": message
        })

    # LOCATION
    def send_location(self, lat, lng, role="customer"):
        return self._post("/location/update/", {
            "lat": lat,
            "lng": lng,
            "role": role
        })