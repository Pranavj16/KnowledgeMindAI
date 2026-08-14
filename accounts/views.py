from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        email_or_user = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        
        if not email_or_user or not password:
            messages.error(request, "Please provide both email and password.")
            return render(request, "accounts/auth.html", {"mode": "login", "email": email_or_user})

        user = authenticate(request, username=email_or_user, password=password)
        if user is None:
            user = authenticate(request, username=email_or_user.lower(), password=password)
        if user is None:
            try:
                matched_user = User.objects.filter(email__iexact=email_or_user).first()
                if matched_user:
                    user = authenticate(request, username=matched_user.username, password=password)
            except Exception:
                pass

        if user is not None:
            login(request, user)
            if not request.POST.get("remember"):
                request.session.set_expiry(0)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect("dashboard")
        messages.error(request, "Invalid email/username or password.")
    return render(request, "accounts/auth.html", {"mode": "login"})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")
        if not name or not email or not password:
            messages.error(request, "Complete all required fields.")
        elif len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
        elif password != confirm:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username__iexact=email).exists() or User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with that email already exists.")
        else:
            user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("dashboard")
    return render(request, "accounts/auth.html", {"mode": "register"})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect("login")


@login_required(login_url="login")
def profile_view(request):
    return render(request, "app/profile.html")
