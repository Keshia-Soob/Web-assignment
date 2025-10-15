# meals/context_processors.py

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
    READ-ONLY: provides `cart_count` to templates.
    Works whether session['cart'] stores ints or legacy dicts.
    DO NOT mutate request.session here.
    """
    cart = request.session.get("cart") or {}
    count = 0
    if isinstance(cart, dict):
        for v in cart.values():
            count += _normalize_qty(v)
    return {"cart_count": count}
