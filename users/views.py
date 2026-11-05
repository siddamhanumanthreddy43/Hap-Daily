from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import CustomerRegistrationForm, CustomerLoginForm, CustomerProfileForm, OwnerRegistrationForm
from .models import CustomUser


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Arokya Milk Store, {user.first_name or user.username}! Your customer account is ready.")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, "Please fix the errors below to register.")
    else:
        form = CustomerRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def owner_register_view(request):
    """
    Dedicated New Store Owner / Manager Registration View
    Creates an account with role='OWNER' and redirects to the owner dashboard.
    """
    if request.user.is_authenticated:
        if request.user.is_owner_user:
            return redirect('owner_dashboard')
        # If currently logged in as customer, sign them out first so they can create an owner account
        logout(request)

    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome Store Owner {user.first_name or user.username}! Your Arokya Milk Store manager portal is now active.")
            return redirect('owner_dashboard')
        else:
            messages.error(request, "Please fix the errors below to complete owner registration.")
    else:
        form = OwnerRegistrationForm()

    return render(request, 'users/owner_register.html', {'form': form})


def customer_login_view(request):
    """
    Dedicated Customer Login Section
    Allows customers to sign in using username, phone number, or email.
    """
    if request.user.is_authenticated:
        if request.user.is_owner_user:
            return redirect('owner_dashboard')
        return redirect('home')

    if request.method == 'POST':
        login_identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Lookup by username, email, or phone
        user_candidate = CustomUser.objects.filter(
            Q(username__iexact=login_identifier) |
            Q(email__iexact=login_identifier) |
            Q(phone=login_identifier)
        ).first()

        target_username = user_candidate.username if user_candidate else login_identifier
        user = authenticate(request, username=target_username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_owner_user:
                return redirect('owner_dashboard')
            return redirect('home')
        else:
            messages.error(request, "Invalid customer credentials. Please check your phone/email and password.")

    return render(request, 'users/customer_login.html', {
        'next': request.GET.get('next', '')
    })


def owner_login_view(request):
    """
    Dedicated Store Owner / Administrator Login Section
    Restricted strictly to users with OWNER or superuser permissions.
    """
    if request.user.is_authenticated:
        if request.user.is_owner_user:
            return redirect('owner_dashboard')
        messages.warning(request, "You are logged in as a Customer. Please log in with Owner credentials.")
        logout(request)

    if request.method == 'POST':
        login_identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user_candidate = CustomUser.objects.filter(
            Q(username__iexact=login_identifier) |
            Q(email__iexact=login_identifier) |
            Q(phone=login_identifier)
        ).first()

        target_username = user_candidate.username if user_candidate else login_identifier
        user = authenticate(request, username=target_username, password=password)

        if user is not None:
            if not user.is_owner_user:
                messages.error(request, "Access Denied: This account does not have Store Owner privileges. Please use the Customer Login section.")
                return redirect('customer_login')
            
            login(request, user)
            messages.success(request, f"Welcome to Store Management, Owner {user.first_name or user.username}!")
            return redirect('owner_dashboard')
        else:
            messages.error(request, "Invalid owner credentials. Please verify your username and password.")

    return render(request, 'users/owner_login.html', {
        'next': request.GET.get('next', '')
    })


def login_view(request):
    """
    Unified entry point - redirects based on tab or role query parameter
    """
    role = request.GET.get('role', 'customer')
    if role == 'owner':
        return owner_login_view(request)
    return customer_login_view(request)


def logout_view(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect('home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your delivery address and details have been updated.")
            return redirect('profile')
    else:
        form = CustomerProfileForm(instance=request.user)

    return render(request, 'users/profile.html', {'form': form})
