from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.views.generic import ListView
from .models import MenuItem

class MenuListView(ListView):
    model = MenuItem
    template_name = 'meals/menu.html'
    context_object_name = 'menu_items'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all menu items grouped by cuisine
        cuisines = MenuItem.objects.values_list('cuisine', flat=True).distinct().order_by('cuisine')
        
        # Create a dictionary with cuisine as key and items as value
        menu_by_cuisine = {}
        for cuisine in cuisines:
            items = MenuItem.objects.filter(cuisine=cuisine).order_by('name')
            if items.exists():
                menu_by_cuisine[cuisine] = items
        
        context['menu_by_cuisine'] = menu_by_cuisine
        context['cuisines'] = cuisines
        
        # Add cuisine choices for the dropdown
        context['cuisine_choices'] = MenuItem.CUISINE_CHOICES
        
        return context

def menu(request):
    # Get all menu items grouped by cuisine
    cuisines = MenuItem.objects.values_list('cuisine', flat=True).distinct().order_by('cuisine')
    
    # Create a dictionary with cuisine as key and items as value
    menu_by_cuisine = {}
    for cuisine in cuisines:
        items = MenuItem.objects.filter(cuisine=cuisine).order_by('name')
        if items.exists():
            menu_by_cuisine[cuisine] = items
    
    return render(request, "meals/menu.html", {
        "menu_by_cuisine": menu_by_cuisine,
        "cuisines": cuisines,
        "cuisine_choices": MenuItem.CUISINE_CHOICES
    })

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

