from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if not request.POST.get("remember"):
                request.session.set_expiry(0)
            return redirect("dashboard")
        messages.error(request, "We couldn't sign you in with those details.")
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
        elif password != confirm:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=email).exists():
            messages.error(request, "An account with that email already exists.")
        else:
            user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
            login(request, user)
            return redirect("dashboard")
    return render(request, "accounts/auth.html", {"mode": "register"})


def logout_view(request):
    logout(request)
    return redirect("landing")


def profile_view(request):
    return render(request, "app/profile.html")
