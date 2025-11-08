# meals/context_processors.py
from .models import MenuItem

def _normalize_qty(v):
    """
    Accept int/str/dict variants and return a positive int.
    We won't write back to the session here.
    """
    if isinstance(v, int):
        return max(1, v)
    if isinstance(v, str):
        try:
            return max(1, int(v))
        except ValueError:
            return 1
    if isinstance(v, dict):
        for key in ("quantity", "qty", "q"):
            if key in v:
                try:
                    return max(1, int(v[key]))
                except (TypeError, ValueError):
                    break
        return 1
    return 1

def cart_context(request):
    """
    Provides cart data to all templates.
    Converts integer cart format { '2': 3 } to dict format
    { '2': {'name': 'Butter Chicken', 'price': 250, 'quantity': 3} }
    """
    raw_cart = request.session.get("cart") or {}
    cart_count = 0
    cart_data = {}
    subtotal = 0
    
    if isinstance(raw_cart, dict) and raw_cart:
        # Get all items from database
        item_ids = [int(k) for k in raw_cart.keys()]
        items = MenuItem.objects.filter(id__in=item_ids)
        
        # Create enriched cart data
        for item in items:
            item_id_str = str(item.id)
            quantity = _normalize_qty(raw_cart.get(item_id_str, 1))
            
            cart_data[item_id_str] = {
                'name': item.name,
                'price': float(item.price),
                'quantity': quantity,
                'image': item.display_image_url
            }
            
            cart_count += quantity
            subtotal += float(item.price) * quantity
    
    return {
        "cart_count": cart_count,
        "cart": cart_data,
        "subtotal": subtotal
    }