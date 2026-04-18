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

    def _get(self, path, params=None):
        try:
            r = requests.get(f"{BASE_URL}{path}", params=params, headers=self._h(), timeout=8)
            return r.json(), r.status_code
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot reach the server.\n\nMake sure Django is running:\npython manage.py runserver"}, 0
        except Exception as e:
            return {"error": str(e)}, 0

    def _post(self, path, data=None):
        try:
            r = requests.post(f"{BASE_URL}{path}", json=data or {}, headers=self._h(), timeout=8)
            return r.json(), r.status_code
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot reach the server.\n\nMake sure Django is running:\npython manage.py runserver"}, 0
        except Exception as e:
            return {"error": str(e)}, 0

    # Auth
    def login(self, username, password):
        data, code = self._post("/auth/login/", {"username": username, "password": password})
        if code == 200:
            self.token = data.get("token")
            self.username = data.get("username")
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
        if search:  p["search"] = search
        return self._get("/menu/", p)

    def get_nearby_menu(self, lat, lng, radius_km=10):
        return self._get("/menu/nearby/", {"lat": lat, "lng": lng, "radius_km": radius_km})

    # Cart
    def get_cart(self):          return self._get("/cart/")
    def add_to_cart(self, iid):  return self._post("/cart/add/", {"item_id": iid})
    def remove_from_cart(self, iid): return self._post("/cart/remove/", {"item_id": iid})

    # Orders
    def place_order(self, name, lat=None, lng=None):
        return self._post("/orders/place/", {
            "client_name": name,
            "delivery_lat": lat,
            "delivery_lng": lng
        })

    def get_orders(self):        return self._get("/orders/")

    # Reviews
    def get_reviews(self):       return self._get("/reviews/")
    def post_review(self, rating, message):
        return self._post("/reviews/create/", {"rating": rating, "message": message})

    # Location
    def send_location(self, lat, lng, role="customer"):
        return self._post("/location/update/", {"lat": lat, "lng": lng, "role": role})

    # HomeCook
    def get_homecook_items(self):   return self._get("/homecook/items/")
    def accept_item(self, item_id): return self._post(f"/homecook/accept/{item_id}/")
    def mark_ready(self, item_id):  return self._post(f"/homecook/ready/{item_id}/")
    def mark_delivered(self, item_id): return self._post(f"/homecook/delivered/{item_id}/")