from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from meals.models import MenuItem

# ---------- Helpers ----------

def _get_cart(request):
    """
    Cart in session should be { "item_id_str": quantity_int, ... }.
    But older/bad entries might be dicts. We normalize on read.
    """
    cart = request.session.get("cart", {})
    normalized = _normalize_cart(cart)
    if normalized != cart:
        request.session["cart"] = normalized
        request.session.modified = True
    return normalized

def _normalize_qty(q):
    """
    Accept int, str, or dict like {"quantity": 2} / {"qty": "3"}.
    Fallback to 1 if we can't parse.
    """
    if isinstance(q, int):
        return max(1, q)
    if isinstance(q, str):
        try:
            return max(1, int(q))
        except ValueError:
            return 1
    if isinstance(q, dict):
        for key in ("quantity", "qty", "q"):
            if key in q:
                try:
                    return max(1, int(q[key]))
                except (TypeError, ValueError):
                    break
        return 1
    return 1

def _normalize_cart(cart):
    """
    Ensure all values are plain positive ints; drop invalids.
    """
    out = {}
    for k, v in cart.items():
        try:
            item_id_str = str(int(k))  # ensure numeric keys only
        except (TypeError, ValueError):
            continue
        qty = _normalize_qty(v)
        if qty > 0:
            out[item_id_str] = qty
    return out

def _cart_items_and_totals(cart):
    """
    Build items + subtotal from a normalized cart.
    """
    items = []
    subtotal = Decimal("0")
    for item_id_str, qty in cart.items():
        item = get_object_or_404(MenuItem, id=int(item_id_str))
        qty = int(qty)
        line_total = (item.price or Decimal("0")) * qty
        subtotal += line_total
        items.append({
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "image": item.display_image_url,
            "price": item.price,
            "quantity": qty,
            "total": line_total,
        })
    return items, subtotal

# ---------- Pages ----------

def order(request):
    return render(request, 'orders/order.html')

def order_confirmed(request):
    return render(request, 'orders/order_confirmed.html')

def order_summary(request):
    cart = _get_cart(request)
    items, subtotal = _cart_items_and_totals(cart)
    context = {
        "items": items,
        "subtotal": subtotal,
        "total": subtotal,  # no tax/shipping
    }
    return render(request, 'orders/order_summary.html', context)

# ---------- Cart endpoints ----------

@require_POST
def update_quantity(request, item_id):
    """
    Supports two modes:
      - POST action=inc/dec
      - POST quantity=<int>
    """
    cart = _get_cart(request)
    key = str(item_id)
    action = request.POST.get("action")

    if action == "inc":
        cart[key] = cart.get(key, 0) + 1
    elif action == "dec":
        current = cart.get(key, 0)
        if current > 1:
            cart[key] = current - 1
        else:
            cart.pop(key, None)
    else:
        qty = _normalize_qty(request.POST.get("quantity", 1))
        if qty <= 0:
            cart.pop(key, None)
        else:
            cart[key] = qty

    request.session["cart"] = cart
    request.session.modified = True
    return redirect("order_summary")

@require_POST
def remove_from_order(request, item_id):
    cart = _get_cart(request)
    cart.pop(str(item_id), None)
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("order_summary")

@require_POST
def clear_order(request):
    request.session["cart"] = {}
    request.session.modified = True
    return redirect("order_summary")

@require_POST
def add_to_order(request, item_id):
    # ensure the item exists
    get_object_or_404(MenuItem, id=item_id)
    cart = _get_cart(request)
    key = str(item_id)
    cart[key] = cart.get(key, 0) + 1
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("order_summary")
