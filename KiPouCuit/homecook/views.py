from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.auth.decorators import login_required   # 🔹 NEW

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


@login_required(login_url='login')   # 🔹 MUST be logged in as a normal user first
def homecook(request):
    """
    HomeCook signup view:
    - User must be authenticated (normal Django User)
    - Requires a valid invite/access code
    - Creates the HomeCook profile
    """
    if request.method == 'POST':
        # ---------- ACCESS CODE CHECK ----------
        invite_code = (request.POST.get('inviteCode') or '').strip()
        expected_code = getattr(settings, "HOMECOOK_ACCESS_CODE", "HOMECOOK2025")

        if invite_code != expected_code:
            messages.error(request, "Invalid access code. Account was not created.")
            return redirect('homecook')

        # ---------- NORMAL SIGNUP FIELDS ----------
        # Force email from logged-in user, not from arbitrary POST
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

        # Sanity: no email on user account = trash setup
        if not email:
            messages.error(request, "Your user account has no email set. Please update your profile first.")
            return redirect('homecook')

        # Block duplicate HomeCook for same email
        if HomeCook.objects.filter(email=email).exists():
            messages.error(request, "A HomeCook account already exists for this user.")
            return redirect('homecook')

        # Validate cuisine choice (if choices defined on model)
        valid_codes = {c[0] for c in getattr(HomeCook, "CUISINE_CHOICES", [])}
        if valid_codes and cuisine not in valid_codes:
            messages.error(request, "Invalid cuisine selected.")
            return redirect('homecook')

        # Create HomeCook
        hc = HomeCook.objects.create(
            name=name,
            surname=surname,
            email=email,
            password=password,  # NOTE: plain-text; for production use Django's User auth
            phone=phone,
            address=address,
            cuisine=cuisine,
            bio=bio,
            profile_picture=profile_picture
        )

        # Persist "logged in" HomeCook in session for kitchen view
        request.session['homecook_email'] = hc.email
        request.session.modified = True

        messages.success(request, "Your Home Cook account has been created successfully!")
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


def homecook_log(request):
    cook = _get_active_homecook(request)
    if not cook:
        messages.info(request, "Create your HomeCook profile first.")
        return render(request, "homecook/homecook_log.html", {"homecook": None, "items": []})

    items = (
        OrderItem.objects
        .select_related("menu_item", "prepared_by")  # removed "order"
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