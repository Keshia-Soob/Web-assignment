from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from .models import Category, MenuItem

# ---------------------------
# MAPPINGS
# ---------------------------
TYPE_MAP = {
    "starters": "Starters",
    "main-courses": "Main Courses",
    "seafood": "Seafood Specialties",
    "desserts": "Desserts",
}

# ---------------------------
# MENU PAGE
# ---------------------------
def menu(request):
    categories = Category.objects.prefetch_related("items").all()
    return render(request, "meals/menu.html", {"categories": categories})

# ---------------------------
# ADD MENU ITEM (ADMIN/FORM)
# ---------------------------
def addmenu(request):
    def _form_data():
        return {
            "itemName": request.POST.get("itemName", "").strip(),
            "itemPrice": request.POST.get("itemPrice", "").strip(),
            "itemDescription": request.POST.get("itemDescription", "").strip(),
            "itemCuisine": request.POST.get("itemCuisine", "").strip(),
            "itemType": request.POST.get("itemType", "").strip(),
        }

    if request.method == "POST":
        errors = []
        data = _form_data()

        # Validate
        for field, label in [
            ("itemName", "Item name"),
            ("itemPrice", "Price"),
            ("itemDescription", "Description"),
            ("itemCuisine", "Cuisine"),
            ("itemType", "Dish type"),
        ]:
            if not data[field]:
                errors.append(f"{label} is required.")

        # Price
        price_val = None
        if data["itemPrice"]:
            try:
                price_val = Decimal(data["itemPrice"])
            except InvalidOperation:
                errors.append("Price must be a valid number (e.g., 650).")

        # Cuisine check
        valid_cuisines = dict(MenuItem.CUISINE_CHOICES)
        if data["itemCuisine"] and data["itemCuisine"] not in valid_cuisines:
            errors.append("Invalid cuisine type selected.")

        # Category
        cat_name = TYPE_MAP.get(data["itemType"])
        if not cat_name:
            errors.append("Invalid dish type selected.")

        if not errors:
            category, _ = Category.objects.get_or_create(name=cat_name)
            image_file = request.FILES.get("itemImage")

            item = MenuItem(
                category=category,
                name=data["itemName"],
                price=price_val or Decimal("0"),
                description=data["itemDescription"],
                cuisine=data["itemCuisine"],
            )
            if image_file:
                item.image = image_file
            item.save()

            return render(
                request,
                "meals/addmenu.html",
                {
                    "success": True,
                    "cuisine_choices": MenuItem.CUISINE_CHOICES,
                    "form_data": {},
                },
            )

        # If errors
        return render(
            request,
            "meals/addmenu.html",
            {
                "errors": errors,
                "form_data": data,
                "cuisine_choices": MenuItem.CUISINE_CHOICES,
            },
        )

    return render(
        request,
        "meals/addmenu.html",
        {
            "cuisine_choices": MenuItem.CUISINE_CHOICES,
            "form_data": {},
        },
    )

# ---------------------------
# ADD TO CART
# ---------------------------
def add_to_cart(request, item_id):
    """Adds an item to the cart — keeps cart format { '2': 1 }."""
    item = get_object_or_404(MenuItem, id=item_id)
    cart = request.session.get("cart", {})

    item_id_str = str(item_id)

    # Convert old dict-style to int
    current_val = cart.get(item_id_str, 0)
    if isinstance(current_val, dict):
        current_val = current_val.get("quantity", 1)

    # Increment or set quantity
    new_qty = int(current_val) + 1
    cart[item_id_str] = new_qty

    request.session["cart"] = cart
    request.session.modified = True

    # Compute subtotal for AJAX
    items = MenuItem.objects.filter(id__in=[int(k) for k in cart.keys()])
    cart_subtotal = sum(float(i.price) * cart[str(i.id)] for i in items)
    cart_count = sum(cart.values())

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "cart_count": cart_count,
            "cart_subtotal": cart_subtotal
        })

    return redirect(reverse("menu"))

# ---------------------------
# REMOVE FROM CART
# ---------------------------
def remove_from_cart(request, item_id):
    """Removes an item from the cart."""
    cart = request.session.get("cart", {})
    item_id_str = str(item_id)

    if item_id_str in cart:
        del cart[item_id_str]
        request.session["cart"] = cart
        request.session.modified = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        cart_count = sum(cart.values())
        cart_subtotal = 0
        if cart:
            items = MenuItem.objects.filter(id__in=[int(k) for k in cart.keys()])
            cart_subtotal = sum(float(i.price) * cart[str(i.id)] for i in items)
        return JsonResponse({
            "success": True,
            "cart_count": cart_count,
            "cart_subtotal": cart_subtotal
        })

    return redirect("order_summary")

# ---------------------------
# VIEW CART
# ---------------------------
def view_cart(request):
    cart = request.session.get("cart", {})
    items = MenuItem.objects.filter(id__in=[int(k) for k in cart.keys()])
    subtotal = sum(float(i.price) * cart[str(i.id)] for i in items)
    return render(request, "cart.html", {"cart": cart, "items": items, "subtotal": subtotal})

# ---------------------------
# CLEAR CART
# ---------------------------
def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True, "cart_count": 0})
    return redirect(reverse("menu"))

# ---------------------------
# CART DATA (AJAX)
# ---------------------------
def get_cart_data(request):
    cart = request.session.get("cart", {})
    items = MenuItem.objects.filter(id__in=[int(k) for k in cart.keys()])
    cart_subtotal = sum(float(i.price) * cart[str(i.id)] for i in items)
    cart_count = sum(cart.values())
    return JsonResponse({
        "cart_count": cart_count,
        "cart_subtotal": cart_subtotal,
        "cart_items": cart,
    })

