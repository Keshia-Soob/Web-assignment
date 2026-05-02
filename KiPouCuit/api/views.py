import math
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from meals.models import MenuItem
from orders.models import Order, OrderItem
from homecook.models import HomeCook
from reviews.models import Review

from .serializers import (
    MenuItemSerializer, OrderSerializer,
    ReviewSerializer, HomeCookSerializer, RegisterSerializer,
)
class IsHomeCook(BasePermission):
    """Allows access only to users that have a HomeCook profile."""
    message = "You must be a registered home cook to perform this action."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            HomeCook.objects.filter(user=request.user).exists()
        )

class IsAdminOrReadOnly(BasePermission):
    """Staff users can write; everyone else is read-only."""
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user and request.user.is_staff

def _haversine(lat1, lng1, lat2, lng2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


CUISINE_EMOJI = {
    "indian":    "🍛",
    "mauritian": "🌴",
    "english":   "🍲",
    "french":    "🥐",
    "asian":     "🥢",
}

@api_view(["POST"])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"error": "Invalid credentials"}, status=400)

    token, _ = Token.objects.get_or_create(user=user)
    is_homecook = HomeCook.objects.filter(user=user).exists()

    return Response({
        "token":       token.key,
        "username":    user.username,
        "user_id":     user.id,
        "first_name":  user.first_name,
        "last_name":   user.last_name,
        "is_homecook": is_homecook,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """POST /api/auth/logout/ – invalidates the current token."""
    request.auth.delete()
    return Response({"detail": "Logged out successfully."})


@api_view(["POST"])
@permission_classes([AllowAny])
def api_register(request):
    """
    POST /api/auth/register/
    Body: { "first_name", "last_name", "email", "password", "phone", "address" }
    Validates with RegisterSerializer then issues a token.
    """
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    user  = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "token":       token.key,
        "user_id":     user.id,
        "username":    user.username,
        "is_homecook": False,
    }, status=201)

@api_view(["GET", "POST"])
@permission_classes([AllowAny])         
@parser_classes([MultiPartParser, FormParser, JSONParser])
def api_menu_list(request):
    if request.method == "GET":
        qs = MenuItem.objects.all()

        cuisine = request.query_params.get("cuisine")
        if cuisine:
            qs = qs.filter(cuisine__iexact=cuisine)

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)

        serializer = MenuItemSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response(
            {"error": "Authentication required. Please log in."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not HomeCook.objects.filter(user=request.user).exists():
        return Response(
            {"error": "Only registered home cooks can add menu items."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = MenuItemSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def api_menu_detail(request, item_id):
    item = get_object_or_404(MenuItem, pk=item_id)

    if request.method == "GET":
        serializer = MenuItemSerializer(item, context={"request": request})
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response(
            {"error": "Authentication required."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not HomeCook.objects.filter(user=request.user).exists():
        return Response(
            {"error": "Only registered home cooks can modify menu items."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "DELETE":
        item.delete()
        return Response(
            {"detail": "Menu item deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )

    partial = (request.method == "PATCH")
    serializer = MenuItemSerializer(
        item, data=request.data, partial=partial,
        context={"request": request},
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@require_GET
def api_menu_nearby(request):
    """
    GET /api/menu/nearby/?lat=&lng=&radius=
    Returns nearby home cooks + their menu items based on GPS distance.
    No authentication required.
    """
    try:
        user_lat = float(request.GET["lat"])
        user_lng = float(request.GET["lng"])
    except (KeyError, ValueError):
        return JsonResponse(
            {"error": "Missing or invalid 'lat' / 'lng' query parameters."},
            status=400,
        )

    radius_km = float(request.GET.get("radius", 20))

    cooks_qs = HomeCook.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
    ).select_related("user")

    cooks_with_distance = [
        (cook, _haversine(user_lat, user_lng, cook.latitude, cook.longitude))
        for cook in cooks_qs
    ]
    cooks_with_distance = [
        (c, d) for c, d in cooks_with_distance if d <= radius_km
    ]
    cooks_with_distance.sort(key=lambda x: x[1])

    if not cooks_with_distance:
        return JsonResponse(
            {"error": f"No home cooks found within {radius_km} km."},
            status=404,
        )

    nearest_cook = cooks_with_distance[0][0]

    result = []
    for cook, dist in cooks_with_distance:
        profile_pic = None
        if cook.profile_picture:
            profile_pic = request.build_absolute_uri(cook.profile_picture.url)

        result.append({
            "id":             cook.id,
            "name":           f"{cook.name} {cook.surname}",
            "cuisine":        cook.cuisine,
            "cuisine_label":  cook.get_cuisine_display(),
            "cuisine_emoji":  CUISINE_EMOJI.get(cook.cuisine, "🍽️"),
            "distance_km":    round(dist, 2),
            "address":        cook.address or "Mauritius",
            "phone":          cook.phone or "",
            "bio":            cook.bio or "",
            "profile_picture": profile_pic,
            "location": {"lat": cook.latitude, "lng": cook.longitude},
        })

    return JsonResponse({
        "suggested_cuisine": nearest_cook.cuisine,
        "suggested_emoji":   CUISINE_EMOJI.get(nearest_cook.cuisine, "🍽️"),
        "user_location":     {"lat": user_lat, "lng": user_lng},
        "nearest_cooks":     result,
        "radius_km":         radius_km,
        "total_found":       len(result),
    })

@api_view(["GET"])
@permission_classes([AllowAny])
def api_cart_view(request):
    """GET /api/cart/ – returns the session cart with full item details as JSON."""
    cart     = request.session.get("cart", {})
    items    = []
    subtotal = 0.0

    for item_id_str, qty in cart.items():
        try:
            item = MenuItem.objects.get(pk=int(item_id_str))
            line  = float(item.price) * int(qty)
            subtotal += line
            items.append({
                "item_id":   item.id,
                "name":      item.name,
                "price":     float(item.price),
                "quantity":  int(qty),
                "line_total": line,
                "image_url": item.display_image_url,
            })
        except MenuItem.DoesNotExist:
            pass

    return Response({"items": items, "subtotal": subtotal, "count": len(items)})


@api_view(["POST"])
@permission_classes([AllowAny])
def api_cart_add(request):
    """
    POST /api/cart/add/
    Body: { "item_id": 3, "quantity": 1 }
    Called via jQuery $.ajax() – demonstrates JSON consumption on the client side.
    """
    item_id  = request.data.get("item_id")
    quantity = int(request.data.get("quantity", 1))

    if not MenuItem.objects.filter(pk=item_id).exists():
        return Response({"error": "Item not found"}, status=404)

    cart     = request.session.get("cart", {})
    key      = str(item_id)
    cart[key] = int(cart.get(key, 0)) + quantity
    request.session["cart"]    = cart
    request.session.modified   = True

    return Response({"success": True, "cart_count": sum(cart.values())})


@api_view(["POST"])
@permission_classes([AllowAny])
def api_cart_remove(request):
    """
    POST /api/cart/remove/
    Body: { "item_id": 3 }
    """
    item_id = str(request.data.get("item_id", ""))
    cart    = request.session.get("cart", {})
    cart.pop(item_id, None)
    request.session["cart"]  = cart
    request.session.modified = True
    return Response({"success": True, "cart_count": sum(cart.values())})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_place_order(request):
    """
    POST /api/orders/place/
    Converts the current session cart into a persisted Order.
    Requires authentication (token or session).
    """
    cart = request.session.get("cart", {})
    if not cart:
        return Response({"error": "Cart is empty"}, status=400)

    client_name = request.data.get(
        "client_name",
        request.user.get_full_name() or request.user.username,
    )

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
        return Response({"error": "No valid items in cart"}, status=400)

    order = Order.objects.create(
        client_name=client_name,
        user=request.user,
    )
    order.items.set(order_items)
    order.save()

    request.session["cart"]  = {}
    request.session.modified = True

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_order_list(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items__menu_item")
        .order_by("-created_at")
    )
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return Response({
        "order_id":    order.id,
        "status":      order.status,
        "human_status": order.human_readable_status,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def api_cooks_list(request):
    cooks = HomeCook.objects.all()
    serializer = HomeCookSerializer(cooks, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def api_reviews_list(request):
    reviews    = Review.objects.order_by("-id")
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_reviews_create(request):
    user = request.user


    has_delivered = any(
        set(order.items.values_list("status", flat=True)) == {OrderItem.Status.DELIVERED}
        for order in Order.objects.filter(user=user).prefetch_related("items")
    )

    if not has_delivered:
        return Response(
            {"error": "You need at least one fully-delivered order to post a review."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(
            first_name=user.first_name or user.username,
            last_name=user.last_name  or "",
            email=user.email,
        )
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_location_update(request):
    lat  = request.data.get("lat")
    lng  = request.data.get("lng")
    role = request.data.get("role", "customer")

    if lat is None or lng is None:
        return Response({"error": "lat and lng are required"}, status=400)

    if role == "cook":
        try:
            cook = request.user.homecook
            cook.latitude  = float(lat)
            cook.longitude = float(lng)
            cook.save(update_fields=["latitude", "longitude"])
        except HomeCook.DoesNotExist:
            return Response({"error": "No HomeCook profile for this user."}, status=403)

    return Response({
        "received": True,
        "lat":      lat,
        "lng":      lng,
        "role":     role,
    })



@api_view(["GET"])
@permission_classes([IsAuthenticated, IsHomeCook])
def api_homecook_items(request):
    cook = request.user.homecook

    available = (
        OrderItem.objects
        .select_related("menu_item")
        .filter(menu_item__cuisine=cook.cuisine, status=OrderItem.Status.PENDING)
        .order_by("created_at")
    )

    my_items = (
        OrderItem.objects
        .select_related("menu_item")
        .filter(
            prepared_by=cook,
            status__in=[OrderItem.Status.ACCEPTED, OrderItem.Status.DELIVERING],
        )
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

    cook_data = HomeCookSerializer(cook, context={"request": request}).data
    return Response({
        "cook":      cook_data,
        "available": [_item_dict(i) for i in available],
        "my_items":  [_item_dict(i) for i in my_items],
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsHomeCook])
def api_accept_item(request, item_id):
    cook = request.user.homecook
    item = get_object_or_404(OrderItem, pk=item_id, status=OrderItem.Status.PENDING)
    item.status      = OrderItem.Status.ACCEPTED
    item.prepared_by = cook
    item.save()
    return Response({"success": True, "status": item.status})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsHomeCook])
def api_mark_ready(request, item_id):    
    cook = request.user.homecook
    item = get_object_or_404(
        OrderItem, pk=item_id,
        prepared_by=cook, status=OrderItem.Status.ACCEPTED,
    )
    item.status = OrderItem.Status.DELIVERING
    item.save()
    return Response({"success": True, "status": item.status})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsHomeCook])
def api_mark_delivered(request, item_id):
    cook = request.user.homecook
    item = get_object_or_404(
        OrderItem, pk=item_id,
        prepared_by=cook, status=OrderItem.Status.DELIVERING,
    )
    item.status = OrderItem.Status.DELIVERED
    item.save()
    return Response({"success": True, "status": item.status})