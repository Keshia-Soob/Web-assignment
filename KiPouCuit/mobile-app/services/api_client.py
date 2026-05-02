import requests

BASE_URL = "http://127.0.0.1:8000/api"


class ApiClient:
    def __init__(self):
        self.token = None
        self.username = None
        self.is_homecook = False
        self._session = requests.Session()  # persists session cookies for cart

    def _h(self):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Token {self.token}"
        return h

    def _get(self, path, params=None):
        try:
            r = self._session.get(
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

    def _post(self, path, data=None):
        try:
            r = self._session.post(
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


    def get_cart(self):
        return self._get("/cart/")

    def add_to_cart(self, iid):
        return self._post("/cart/add/", {"item_id": iid})

    def decrease_cart_item(self, iid):
        return self._post("/cart/add/", {"item_id": iid, "quantity": -1})

    def remove_from_cart(self, iid):
        return self._post("/cart/remove/", {"item_id": iid})


    def place_order(self, name, lat=None, lng=None):
        return self._post("/orders/place/", {
            "client_name": name,
            "delivery_lat": lat,
            "delivery_lng": lng
        })

    def get_orders(self):
        return self._get("/orders/")

    def get_reviews(self):
        return self._get("/reviews/")

    def post_review(self, rating, message):
        return self._post("/reviews/create/", {
            "rating": rating,
            "message": message
        })


    def get_homecook_dashboard(self):
        return self._get("/homecook/items/")

    def send_location(self, lat, lng, role="customer"):
        return self._post("/location/update/", {
            "lat": lat,
            "lng": lng,
            "role": role
        })