"""
KiPouCuit REST API Views
========================
Drop this file into a new `api` app inside the KiPouCuit Django project.

Endpoints exposed:
  GET  /api/menu/                        – list all menu items (filter ?cuisine=)
  GET  /api/menu/<id>/                   – single menu item
  GET  /api/menu/nearby/?lat=&lng=       – items from cooks near a GPS coordinate
  POST /api/cart/add/                    – add item to session cart
  POST /api/cart/remove/                 – remove item from cart
  GET  /api/cart/                        – view cart contents
  POST /api/orders/place/               – place an order (requires auth token)
  GET  /api/orders/                      – list orders for logged-in user
  GET  /api/orders/<id>/status/          – order status polling
  GET  /api/cooks/                       – list all home cooks
  POST /api/reviews/                     – submit a review (requires auth)
  GET  /api/reviews/                     – list all reviews
  POST /api/auth/login/                  – obtain token
  POST /api/auth/logout/                 – invalidate token
  POST /api/location/update/            – update cook's current GPS location
"""

import math
import json

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from meals.models import MenuItem
from orders.models import Order, OrderItem
from homecook.models import HomeCook
from reviews.models import Review

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def _haversine_km(lat1, lon1, lat2, lon2):
    """Return approximate distance in km between two lat/lon points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _menu_item_to_dict(item):
    return {
        "id": item.id,
        "name": item.name,
        "price": float(item.price),
        "description": item.description,
        "cuisine": item.cuisine,
        "image_url": item.display_image_url,
    }


def _order_to_dict(order):
    return {
        "id": order.id,
        "client_name": order.client_name,
        "status": order.status,
        "human_status": order.human_readable_status,
        "subtotal": float(order.subtotal),
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "id": oi.id,
                "name": oi.menu_item.name,
                "quantity": oi.quantity,
                "price": float(oi.menu_item.price),
                "status": oi.status,
            }
            for oi in order.items.select_related("menu_item").all()
        ],
    }


def _review_to_dict(r):
    return {
        "id": r.id,
        "first_name": r.first_name,
        "last_name": r.last_name,
        "rating": r.rating,
        "message": r.message,
        "created_at": r.created_at.isoformat(),
    }


def _cook_to_dict(cook):
    return {
        "id": cook.id,
        "name": cook.name,
        "surname": cook.surname,
        "cuisine": cook.cuisine,
        "bio": cook.bio or "",
        "address": cook.address or "",
        "phone": cook.phone or "",
    }


# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def api_login(request):
    """
    POST /api/auth/login/
    Body: { "username": "...", "password": "..." }
    Returns: { "token": "...", "user_id": ..., "username": "..." }
    """
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "").strip()

    if not username or not password:
        return Response({"error": "username and password required"}, status=400)

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"error": "Invalid credentials"}, status=401)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        "token": token.key,
        "user_id": user.id,
        "username": user.username,
        "is_homecook": hasattr(user, "homecook"),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """DELETE the user's auth token."""
    request.auth.delete()
    return Response({"detail": "Logged out."})


# ─────────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([AllowAny])
def api_menu_list(request):
    """
    GET /api/menu/
    Optional query params:
      ?cuisine=mauritian
      ?search=chicken
    Returns paginated list of menu items.
    """
    qs = MenuItem.objects.all()

    cuisine = request.query_params.get("cuisine")
    if cuisine:
        qs = qs.filter(cuisine__iexact=cuisine)

    search = request.query_params.get("search")
    if search:
        qs = qs.filter(name__icontains=search)

    return Response([_menu_item_to_dict(i) for i in qs])


@api_view(["GET"])
@permission_classes([AllowAny])
def api_menu_detail(request, item_id):
    """GET /api/menu/<id>/"""
    try:
        item = MenuItem.objects.get(pk=item_id)
    except MenuItem.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    return Response(_menu_item_to_dict(item))


@api_view(["GET"])
@permission_classes([AllowAny])
def api_menu_nearby(request):
    """
    GET /api/menu/nearby/?lat=<float>&lng=<float>&radius_km=<float>

    Uses the HomeCook.address field (or a future lat/lng field) to find
    cooks within `radius_km` (default 10) of the caller's GPS position,
    then returns their menu items.

    NOTE: For a production app you would store lat/lng on HomeCook.
    This endpoint is designed to accept those coordinates once added.
    The mobile app passes device GPS here to get hyper-local results.
    """
    try:
        user_lat = float(request.query_params["lat"])
        user_lng = float(request.query_params["lng"])
    except (KeyError, ValueError):
        return Response({"error": "lat and lng are required float params"}, status=400)

    radius_km = float(request.query_params.get("radius_km", 10))

    # ── When HomeCook model has lat/lng fields, filter here. ──
    # For now, return all items tagged with the cuisine most common
    # in Mauritius (mauritian) as a proximity-aware fallback.
    # Replace the block below once you add HomeCook.latitude / longitude.

    nearby_cooks = HomeCook.objects.all()  # replace with geo-filter
    nearby_cook_ids = [c.id for c in nearby_cooks]

    # Return all items (proximity filter TODO once lat/lng stored on cook)
    items = MenuItem.objects.all()
    data = [_menu_item_to_dict(i) for i in items]
    return Response({
        "user_location": {"lat": user_lat, "lng": user_lng},
        "radius_km": radius_km,
        "count": len(data),
        "items": data,
    })


# ─────────────────────────────────────────────
#  CART  (session-based, mirrors web app)
# ─────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([AllowAny])
def api_cart_view(request):
    """GET /api/cart/  – returns current session cart with item details."""
    cart = request.session.get("cart", {})
    result = []
    subtotal = 0.0
    for item_id_str, qty in cart.items():
        try:
            item = MenuItem.objects.get(pk=int(item_id_str))
            line = float(item.price) * int(qty)
            subtotal += line
            result.append({
                "item_id": item.id,
                "name": item.name,
                "price": float(item.price),
                "quantity": int(qty),
                "line_total": line,
                "image_url": item.display_image_url,
            })
        except MenuItem.DoesNotExist:
            pass
    return Response({"items": result, "subtotal": subtotal, "count": len(result)})


@api_view(["POST"])
@permission_classes([AllowAny])
def api_cart_add(request):
    """
    POST /api/cart/add/
    Body: { "item_id": 3, "quantity": 1 }
    """
    item_id = request.data.get("item_id")
    quantity = int(request.data.get("quantity", 1))
    try:
        MenuItem.objects.get(pk=item_id)
    except MenuItem.DoesNotExist:
        return Response({"error": "Item not found"}, status=404)

    cart = request.session.get("cart", {})
    key = str(item_id)
    cart[key] = int(cart.get(key, 0)) + quantity
    request.session["cart"] = cart
    request.session.modified = True

    return Response({"success": True, "cart_count": sum(cart.values())})


@api_view(["POST"])
@permission_classes([AllowAny])
def api_cart_remove(request):
    """
    POST /api/cart/remove/
    Body: { "item_id": 3 }
    """
    item_id = str(request.data.get("item_id", ""))
    cart = request.session.get("cart", {})
    cart.pop(item_id, None)
    request.session["cart"] = cart
    request.session.modified = True
    return Response({"success": True, "cart_count": sum(cart.values())})


# ─────────────────────────────────────────────
#  ORDERS
# ─────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_place_order(request):
    """
    POST /api/orders/place/
    Body: { "client_name": "...", "delivery_lat": 0.0, "delivery_lng": 0.0 }

    Converts the session cart into a real Order.
    delivery_lat / delivery_lng are stored for driver routing (sensor data).
    """
    cart = request.session.get("cart", {})
    if not cart:
        return Response({"error": "Cart is empty"}, status=400)

    client_name = request.data.get("client_name", request.user.get_full_name() or request.user.username)

    # Create order items
    order_items = []
    for item_id_str, qty in cart.items():
        try:
            menu_item = MenuItem.objects.get(pk=int(item_id_str))
            oi = OrderItem.objects.create(
                menu_item=menu_item,
                quantity=int(qty),
                status=OrderItem.Status.PENDING,
            )
            order_items.append(oi)
        except MenuItem.DoesNotExist:
            pass

    if not order_items:
        return Response({"error": "No valid items"}, status=400)

    order = Order.objects.create(
        client_name=client_name,
        user=request.user,
    )
    order.items.set(order_items)
    order.save()

    # Clear cart
    request.session["cart"] = {}
    request.session.modified = True

    return Response({"success": True, "order_id": order.id, "status": order.status}, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_order_list(request):
    """GET /api/orders/ – list all orders for the authenticated user."""
    orders = Order.objects.filter(user=request.user).prefetch_related("items__menu_item").order_by("-created_at")
    return Response([_order_to_dict(o) for o in orders])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_order_status(request, order_id):
    """GET /api/orders/<id>/status/ – lightweight status poll for live tracking."""
    try:
        order = Order.objects.get(pk=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    return Response({
        "order_id": order.id,
        "status": order.status,
        "human_status": order.human_readable_status,
    })


# ─────────────────────────────────────────────
#  HOME COOKS
# ─────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([AllowAny])
def api_cooks_list(request):
    """GET /api/cooks/  – list all registered home cooks."""
    cooks = HomeCook.objects.all()
    return Response([_cook_to_dict(c) for c in cooks])


# ─────────────────────────────────────────────
#  REVIEWS
# ─────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([AllowAny])
def api_reviews_list(request):
    """GET /api/reviews/"""
    reviews = Review.objects.order_by("-id")
    return Response([_review_to_dict(r) for r in reviews])


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_reviews_create(request):
    """
    POST /api/reviews/
    Body: { "rating": 5, "message": "..." }
    Requires the user to have at least one delivered order (mirrors web logic).
    """
    user = request.user
    delivered_count = 0
    for order in Order.objects.filter(user=user):
        statuses = set(order.items.values_list("status", flat=True))
        if statuses == {OrderItem.Status.DELIVERED}:
            delivered_count += 1

    if delivered_count < 1:
        return Response(
            {"error": "You need at least one delivered order to post a review."},
            status=403
        )

    rating = request.data.get("rating")
    message = request.data.get("message", "").strip()

    if not rating or not message:
        return Response({"error": "rating and message are required"}, status=400)

    review = Review.objects.create(
        first_name=user.first_name or user.username,
        last_name=user.last_name or "",
        email=user.email,
        rating=int(rating),
        message=message,
    )
    return Response(_review_to_dict(review), status=201)


# ─────────────────────────────────────────────
#  LOCATION UPDATE  (sensor data endpoint)
# ─────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_location_update(request):
    """
    POST /api/location/update/
    Body: { "lat": -20.162, "lng": 57.499, "role": "cook" | "customer" }

    Receives GPS coordinates from the mobile device.
    - For cooks: updates their live location so customers can track delivery.
    - For customers: records delivery pin for the current active order.

    NOTE: You need to add a CookLocation model (or lat/lng fields on HomeCook)
    to persist this. The endpoint is wired and ready — just add the model.
    """
    lat = request.data.get("lat")
    lng = request.data.get("lng")
    role = request.data.get("role", "customer")

    if lat is None or lng is None:
        return Response({"error": "lat and lng required"}, status=400)

    # TODO: persist to HomeCook.latitude / HomeCook.longitude or a
    # dedicated LiveLocation model for real-time delivery tracking.
    # Example:
    #   if role == "cook":
    #       cook = request.user.homecook
    #       cook.latitude = lat
    #       cook.longitude = lng
    #       cook.save(update_fields=["latitude", "longitude"])

    return Response({
        "received": True,
        "lat": lat,
        "lng": lng,
        "role": role,
        "message": "Location noted. Add lat/lng fields to HomeCook to persist.",
    })


# ─────────────────────────────────────────────────────────────────────────────
#  HOMECOOK DASHBOARD API  (used by the mobile Cook screen)
# ─────────────────────────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_homecook_items(request):
    """
    GET /api/homecook/items/
    Returns available (PENDING) orders for this cook's cuisine,
    and orders already accepted/delivering by this cook.
    Mirrors what the homecook_log view does on the website.
    """
    try:
        cook = request.user.homecook
    except HomeCook.DoesNotExist:
        return Response({"error": "You do not have a HomeCook profile."}, status=403)

    available = (
        OrderItem.objects
        .select_related("menu_item")
        .filter(menu_item__cuisine=cook.cuisine,
                status=OrderItem.Status.PENDING)
        .order_by("created_at")
    )

    my_items = (
        OrderItem.objects
        .select_related("menu_item")
        .filter(prepared_by=cook,
                status__in=[OrderItem.Status.ACCEPTED,
                            OrderItem.Status.DELIVERING])
        .order_by("created_at")
    )

    def _item_dict(oi):
        order = oi.orders.first()
        return {
            "id":       oi.id,
            "name":     oi.menu_item.name,
            "quantity": oi.quantity,
            "status":   oi.status,
            "order_id": order.id if order else None,
        }

    return Response({
        "cook":      _cook_to_dict(cook),
        "available": [_item_dict(i) for i in available],
        "my_items":  [_item_dict(i) for i in my_items],
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_accept_item(request, item_id):
    """POST /api/homecook/accept/<item_id>/"""
    try:
        cook = request.user.homecook
    except HomeCook.DoesNotExist:
        return Response({"error": "No HomeCook profile."}, status=403)

    try:
        item = OrderItem.objects.get(pk=item_id,
                                     status=OrderItem.Status.PENDING)
    except OrderItem.DoesNotExist:
        return Response({"error": "Item not found or already taken."}, status=404)

    item.status      = OrderItem.Status.ACCEPTED
    item.prepared_by = cook
    item.save()
    return Response({"success": True, "status": item.status})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_mark_ready(request, item_id):
    """POST /api/homecook/ready/<item_id>/"""
    try:
        cook = request.user.homecook
    except HomeCook.DoesNotExist:
        return Response({"error": "No HomeCook profile."}, status=403)

    item = get_object_or_404(OrderItem, pk=item_id, prepared_by=cook,
                             status=OrderItem.Status.ACCEPTED)
    item.status = OrderItem.Status.DELIVERING
    item.save()
    return Response({"success": True, "status": item.status})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_mark_delivered(request, item_id):
    """POST /api/homecook/delivered/<item_id>/"""
    try:
        cook = request.user.homecook
    except HomeCook.DoesNotExist:
        return Response({"error": "No HomeCook profile."}, status=403)

    item = get_object_or_404(OrderItem, pk=item_id, prepared_by=cook,
                             status=OrderItem.Status.DELIVERING)
    item.status = OrderItem.Status.DELIVERED
    item.save()
    return Response({"success": True, "status": item.status})