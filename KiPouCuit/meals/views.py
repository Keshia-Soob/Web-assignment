from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
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
