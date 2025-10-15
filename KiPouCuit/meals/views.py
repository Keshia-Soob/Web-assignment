from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from .models import Category, MenuItem

# Map your dropdown values to Category names
TYPE_MAP = {
    "starters": "Starters",
    "main-courses": "Main Courses",
    "seafood": "Seafood Specialties",
    "desserts": "Desserts",
}

def menu(request):
    categories = Category.objects.prefetch_related("items").all()
    return render(request, "meals/menu.html", {"categories": categories})

def addmenu(request):
    # Helper to keep user inputs on error
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

        # Basic validation
        for field, label in [
            ("itemName", "Item name"),
            ("itemPrice", "Price"),
            ("itemDescription", "Description"),
            ("itemCuisine", "Cuisine"),
            ("itemType", "Dish type"),
        ]:
            if not data[field]:
                errors.append(f"{label} is required.")

        # Price validation
        price_val = None
        if data["itemPrice"]:
            try:
                price_val = Decimal(data["itemPrice"])
            except InvalidOperation:
                errors.append("Price must be a valid number (e.g., 650).")

        # Cuisine validation
        valid_cuisines = dict(MenuItem.CUISINE_CHOICES)
        if data["itemCuisine"] and data["itemCuisine"] not in valid_cuisines:
            errors.append("Invalid cuisine type selected.")

        # Category mapping
        cat_name = TYPE_MAP.get(data["itemType"])
        if not cat_name:
            errors.append("Invalid dish type selected.")

        if not errors:
            category, _ = Category.objects.get_or_create(name=cat_name)
            image_file = request.FILES.get("itemImage")  # optional

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

            # Show success banner on the same page
            return render(
                request,
                "meals/addmenu.html",
                {
                    "success": True,
                    "cuisine_choices": MenuItem.CUISINE_CHOICES,
                    "form_data": {},
                },
            )

        # Return errors + prefilled data
        return render(
            request,
            "meals/addmenu.html",
            {
                "errors": errors,
                "form_data": data,
                "cuisine_choices": MenuItem.CUISINE_CHOICES,
            },
        )

    # GET
    return render(
        request,
        "meals/addmenu.html",
        {
            "cuisine_choices": MenuItem.CUISINE_CHOICES,
            "form_data": {},
        },
    )

def add_to_cart(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(MenuItem, id=item_id)
        cart = request.session.get('cart', {})

        item_id_str = str(item_id)
        
        if item_id_str in cart:
            cart[item_id_str]['quantity'] += 1
        else:
            cart[item_id_str] = {
                'name': item.name,
                'price': float(item.price),  # Ensure it's serializable
                'quantity': 1
            }

        request.session['cart'] = cart
        request.session.modified = True

        # Calculate updated cart info
        cart_count = sum(item['quantity'] for item in cart.values())
        cart_subtotal = sum(item['price'] * item['quantity'] for item in cart.values())

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'cart_count': cart_count,
                'cart_subtotal': cart_subtotal,
                'success': True
            })

        return redirect(reverse('menu'))
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid request method'}, status=400)
        return redirect(reverse('menu'))

def view_cart(request):
    cart = request.session.get('cart', {})
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'cart.html', {'cart': cart, 'subtotal': subtotal})

def clear_cart(request):
    if request.method == 'POST':
        request.session['cart'] = {}
        request.session.modified = True
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'cart_count': 0})
            
        return redirect(reverse('menu'))
    return redirect(reverse('menu'))

def get_cart_data(request):
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    cart_subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    
    return JsonResponse({
        'cart_count': cart_count,
        'cart_subtotal': cart_subtotal,
        'cart_items': cart
    })

# In meals/views.py

# def remove_from_cart(request, item_id):
#     cart = request.session.get('cart', {})
#     item_id_str = str(item_id)

#     if request.method == 'POST' and item_id_str in cart:
#         del cart[item_id_str]
#         request.session['cart'] = cart
#         request.session.modified = True

#         cart_count = sum(item['quantity'] for item in cart.values())
#         cart_subtotal = sum(item['price'] * item['quantity'] for item in cart.values())

#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'success': True,
#                 'cart_count': cart_count,
#                 'cart_subtotal': cart_subtotal
#             })
#         return redirect('view_cart')

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         return JsonResponse({'success': False, 'error': 'Invalid request'})
#     return redirect('view_cart')

def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        item_id_str = str(item_id)

        if item_id_str in cart:
            del cart[item_id_str]
            request.session['cart'] = cart
            request.session.modified = True

            cart_count = sum(item['quantity'] for item in cart.values())
            cart_subtotal = sum(item['price'] * item['quantity'] for item in cart.values())

            # JSON response for AJAX
            return JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'cart_subtotal': cart_subtotal
            })

    return JsonResponse({'success': False, 'error': 'Item not found in cart'})
