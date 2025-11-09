from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden

from .models import HomeCook
from users.models import UserProfile
from orders.models import OrderItem


def _get_active_homecook(request):
    """
    Return the HomeCook linked to the current request.user, or None.
    Keep a session fallback for backward compatibility.
    """
    if not request.user.is_authenticated:
        return None

    try:
        return request.user.homecook
    except HomeCook.DoesNotExist:
        email = request.session.get("homecook_email")
        if email:
            try:
                return HomeCook.objects.get(email=email)
            except HomeCook.DoesNotExist:
                return None
        return None


@login_required(login_url='login')
def homecook(request):
    """
    Create HomeCook profile for an authenticated user.
    Only HomeCook-specific data is stored here (no plaintext password).
    """
    if hasattr(request.user, "homecook"):
        messages.info(request, "You already have a HomeCook account.")
        return redirect("homecook_log")

    if request.method == 'POST':
        invite_code = (request.POST.get('inviteCode') or '').strip()
        expected_code = getattr(settings, "HOMECOOK_ACCESS_CODE", "HOMECOOK2025")
        if invite_code != expected_code:
            messages.error(request, "Invalid access code. Account was not created.")
            return redirect('homecook')

        user = request.user
        email = (user.email or '').strip().lower()

        name = request.POST.get('name', '').strip() or user.first_name or ""
        surname = request.POST.get('surname', '').strip() or user.last_name or ""
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        cuisine = request.POST.get('cuisine', '')
        bio = request.POST.get('bio', '').strip()
        profile_picture = request.FILES.get('profilePic')

        valid_codes = {c[0] for c in getattr(HomeCook, "CUISINE_CHOICES", [])}
        if valid_codes and cuisine not in valid_codes:
            messages.error(request, "Invalid cuisine selected.")
            return redirect('homecook')

        hc = HomeCook.objects.create(
            user=user,
            name=name,
            surname=surname,
            email=email,
            phone=phone,
            address=address,
            cuisine=cuisine,
            bio=bio,
            profile_picture=profile_picture
        )

        # Optional session key for older flows
        request.session['homecook_email'] = hc.email
        request.session.modified = True

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_homecook = True
        profile.homecook_status = "APPROVED"
        profile.bio = bio
        profile.specialty = cuisine
        profile.save()

        messages.success(request, "Your HomeCook account has been created successfully!")
        return redirect('homecook_log')

    return render(request, 'homecook/homecook.html')


def homecook_signup(request):
    return homecook(request)


def homecook_onboarding(request):
    return render(request, "homecook/homecook_onboarding.html")


@login_required(login_url='login')
def homecook_log(request):
    """
    Show:
      - available_items: PENDING items matching cook cuisine
      - my_items: items assigned to this cook and in ACCEPTED/DELIVERING states
    """
    cook = _get_active_homecook(request)
    if not cook:
        messages.info(request, "Create your HomeCook profile first.")
        return render(request, "homecook/homecook_log.html", {"homecook": None, "available_items": [], "my_items": []})

    available_items = OrderItem.objects.select_related('menu_item').filter(
        menu_item__cuisine=cook.cuisine,
        status=OrderItem.Status.PENDING
    ).order_by('created_at')

    my_items = OrderItem.objects.select_related('menu_item').filter(
        prepared_by=cook,
        status__in=[OrderItem.Status.ACCEPTED, OrderItem.Status.DELIVERING]
    ).order_by('created_at')

    return render(request, "homecook/homecook_log.html", {
        "homecook": cook,
        "available_items": available_items,
        "my_items": my_items,
    })


@require_POST
@login_required(login_url='login')
def accept_order(request, item_id):
    """
    Accept a PENDING OrderItem and assign it to the active cook.
    Uses a transaction + select_for_update to reduce race conditions.
    """
    cook = _get_active_homecook(request)
    if not cook:
        messages.error(request, "Create your HomeCook profile first.")
        return redirect('homecook_log')

    try:
        with transaction.atomic():
            item = OrderItem.objects.select_for_update().select_related('menu_item').get(id=item_id)
            if item.status != OrderItem.Status.PENDING:
                messages.error(request, "This item has already been taken.")
                return redirect('homecook_log')

            item.status = OrderItem.Status.ACCEPTED
            item.prepared_by = cook
            item.save()

            messages.success(request, f"You accepted '{item.menu_item.name}'.")
            return redirect('homecook_log')

    except OrderItem.DoesNotExist:
        messages.error(request, "Order item not found.")
        return redirect('homecook_log')


@require_POST
@login_required(login_url='login')
def mark_ready(request, item_id):
    """
    Mark an accepted item as DELIVERING (ready/out for delivery).
    Only the cook who accepted it can perform this.
    """
    cook = _get_active_homecook(request)
    if not cook:
        messages.error(request, "Create your HomeCook profile first.")
        return redirect('homecook_log')

    item = get_object_or_404(OrderItem, id=item_id)

    if item.prepared_by_id != getattr(cook, 'id', None):
        return HttpResponseForbidden("You are not allowed to update this item.")

    if item.status != OrderItem.Status.ACCEPTED:
        messages.error(request, "Item must be in Accepted state to mark as ready.")
        return redirect('homecook_log')

    item.status = OrderItem.Status.DELIVERING
    item.save()

    messages.success(request, f"Marked '{item.menu_item.name}' as ready (out for delivery).")
    return redirect('homecook_log')


@require_POST
@login_required(login_url='login')
def mark_delivered(request, item_id):
    """
    Mark item as DELIVERED. Only the assigned cook can do this.
    """
    cook = _get_active_homecook(request)
    if not cook:
        messages.error(request, "Create your HomeCook profile first.")
        return redirect('homecook_log')

    item = get_object_or_404(OrderItem, id=item_id)

    if item.prepared_by_id != getattr(cook, 'id', None):
        return HttpResponseForbidden("You are not allowed to update this item.")

    if item.status != OrderItem.Status.DELIVERING:
        messages.error(request, "Item must be 'being delivered' to mark as delivered.")
        return redirect('homecook_log')

    item.status = OrderItem.Status.DELIVERED
    item.save()

    messages.success(request, f"Marked '{item.menu_item.name}' as delivered.")
    return redirect('homecook_log')
