from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .models import HomeCook
from users.models import UserProfile
from orders.models import OrderItem


def _get_active_homecook(request):
    """
    Get the HomeCook linked to the currently logged-in user.
    We no longer trust just session email; we tie it to request.user.
    """
    if not request.user.is_authenticated:
        return None

    # OneToOneField from HomeCook to User
    try:
        return request.user.homecook
    except HomeCook.DoesNotExist:
        # fallback if you still want to support old session logic:
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
    HomeCook signup view:
    - User must be authenticated (normal Django User)
    - Requires a valid invite/access code
    - Creates the HomeCook profile linked to the user
    - Updates UserProfile to mark them as a homecook
    """
    # If user already has a homecook account, don't let them re-register
    if hasattr(request.user, "homecook"):
        messages.info(request, "You already have a HomeCook account.")
        return redirect("homecook_log")

    if request.method == 'POST':
        # ---------- ACCESS CODE CHECK ----------
        invite_code = (request.POST.get('inviteCode') or '').strip()
        expected_code = getattr(settings, "HOMECOOK_ACCESS_CODE", "HOMECOOK2025")

        if invite_code != expected_code:
            messages.error(request, "Invalid access code. Account was not created.")
            return redirect('homecook')

        # ---------- NORMAL SIGNUP FIELDS ----------
        user = request.user
        email = (user.email or '').strip().lower()

        name = request.POST.get('name', '').strip()
        surname = request.POST.get('surname', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        cuisine = request.POST.get('cuisine', '')
        bio = request.POST.get('bio', '').strip()
        profile_picture = request.FILES.get('profilePic')

        # Password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('homecook')

        # Sanity: no email on user account
        if not email:
            messages.error(request, "Your user account has no email set. Please update your profile first.")
            return redirect('homecook')

        # Block duplicate HomeCook for same user
        if HomeCook.objects.filter(user=user).exists():
            messages.error(request, "A HomeCook account already exists for this user.")
            return redirect('homecook')

        # Validate cuisine choice (if defined on model)
        valid_codes = {c[0] for c in getattr(HomeCook, "CUISINE_CHOICES", [])}
        if valid_codes and cuisine not in valid_codes:
            messages.error(request, "Invalid cuisine selected.")
            return redirect('homecook')

        # ---------- CREATE HOMECOOK ----------
        hc = HomeCook.objects.create(
            user=user,
            name=name,
            surname=surname,
            email=email,
            password=password,  # still stored, but REAL login is Django User
            phone=phone,
            address=address,
            cuisine=cuisine,
            bio=bio,
            profile_picture=profile_picture
        )

        # Keep old session logic for compatibility (optional)
        request.session['homecook_email'] = hc.email
        request.session.modified = True

        # ---------- UPDATE USERPROFILE ROLE ----------
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_homecook = True
        profile.homecook_status = "APPROVED"
        profile.bio = bio
        profile.specialty = cuisine
        profile.save()

        messages.success(request, "Your HomeCook account has been created successfully!")
        return redirect('homecook_log')

    # GET -> show form
    return render(request, 'homecook/homecook.html')


def homecook_signup(request):
    """
    Alias for the same signup logic, so /homecook/ and /homecook/signup/
    both hit the same code (and both require login).
    """
    return homecook(request)


def homecook_onboarding(request):
    """
    Static page: explains steps to become a HomeCook.
    """
    return render(request, "homecook/homecook_onboarding.html")


@login_required(login_url='login')
def homecook_log(request):
    """
    HomeCook's "kitchen" log – only for logged-in homecooks.
    Shows pending orders for their cuisine.
    """
    cook = _get_active_homecook(request)
    if not cook:
        messages.info(request, "Create your HomeCook profile first.")
        return render(request, "homecook/homecook_log.html", {"homecook": None, "items": []})

    items = (
        OrderItem.objects
        .select_related("menu_item", "prepared_by")
        .filter(menu_item__cuisine=cook.cuisine, status=OrderItem.Status.PENDING)
        .order_by("created_at")
    )

    return render(request, "homecook/homecook_log.html", {"homecook": cook, "items": items})


@require_POST
@login_required(login_url='login')
def mark_order_ready(request, item_id):
    """
    Only an active HomeCook can mark an order item as READY.
    """
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