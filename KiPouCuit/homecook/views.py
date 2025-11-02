from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import HomeCook
from orders.models import OrderItem  


def _get_active_homecook(request):
    """
    Resolve which HomeCook is "logged in" for this session.
    - Prefer email stored in session (set at signup).
    - Fallback to the first HomeCook if none in session.
    """
    email = request.session.get("homecook_email")
    if email:
        try:
            return HomeCook.objects.get(email=email)
        except HomeCook.DoesNotExist:
            pass

    return HomeCook.objects.first()



def homecook(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        surname = request.POST.get('surname', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        cuisine = request.POST.get('cuisine', '')
        bio = request.POST.get('bio', '').strip()
        profile_picture = request.FILES.get('profilePic')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('homecook')

        if HomeCook.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect('homecook')

        valid_codes = {c[0] for c in getattr(HomeCook, "CUISINE_CHOICES", [])}
        if valid_codes and cuisine not in valid_codes:
            messages.error(request, "Invalid cuisine selected.")
            return redirect('homecook')

        hc = HomeCook.objects.create(
            name=name,
            surname=surname,
            email=email,
            password=password, 
            phone=phone,
            address=address,
            cuisine=cuisine,
            bio=bio,
            profile_picture=profile_picture
        )

    
        request.session['homecook_email'] = hc.email
        request.session.modified = True

        messages.success(request, "Your Home Cook account has been created successfully!")
        return redirect('homecook_log')

    return render(request, 'homecook/homecook.html')


def homecook_log(request):
    cook = _get_active_homecook(request)
    if not cook:
        messages.info(request, "Create your HomeCook profile first.")
        return render(request, "homecook/homecook_log.html", {"homecook": None, "items": []})

    items = (
        OrderItem.objects
        .select_related("menu_item", "prepared_by")  # <-- removed "order"
        .filter(menu_item__cuisine=cook.cuisine, status=OrderItem.Status.PENDING)
        .order_by("created_at")
    )

    return render(request, "homecook/homecook_log.html", {"homecook": cook, "items": items})


@require_POST
def mark_order_ready(request, item_id):
    cook = _get_active_homecook(request)
    if not cook:
        messages.error(request, "No active HomeCook found for this session.")
        return redirect('homecook_log')

    item = get_object_or_404(
        OrderItem,
        id=item_id,
        menu_item__cuisine=cook.cuisine,  
        status=OrderItem.Status.PENDING,    
    )

    item.status = OrderItem.Status.READY
    item.prepared_by = cook
    item.save()

    messages.success(request, f"Marked '{item.menu_item.name}' as ready.")
    return redirect('homecook_log')
