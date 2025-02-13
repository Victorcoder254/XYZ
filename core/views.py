from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .models import User
from .decorators import role_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from core.models import User  # Import your custom User model
from django.contrib import messages


def home_view(request):
    return render(request, "home.html")

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password")
        role = request.POST.get("role")  # Capturing role from the form

        # Validate role
        if role not in ["business_admin", "cpc_admin"]:
            messages.error(request, "Invalid role selected.")
            return render(request, "files/signup.html")

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Choose another one.")
            return render(request, "files/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use. Use another email.")
            return render(request, "files/signup.html")

        # Create user without role first
        user = User.objects.create_user(username=username, email=email, password=password)
        user.role = role  # Assign role manually
        user.save()

        # Log in user
        login(request, user)

        # Redirect based on role
        if role == "business_admin":
            return redirect("business_dashboard")
        else:
            return redirect("cpc_dashboard")

    return render(request, "files/signup.html")


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.role == "business_admin":
                return redirect("business_dashboard")
            elif user.role == "cpc_admin":
                return redirect("cpc_dashboard")
        else:
            return HttpResponse("Invalid credentials")
    return render(request, "files/login.html")


@login_required
@role_required("business_admin")
def business_dashboard(request):
    return HttpResponse("Business Dashboard")
    #return render(request, "business_dashboard.html")

@login_required
@role_required("cpc_admin")
def cpc_dashboard(request):
    return HttpResponse("CPC Dashboard")
    #return render(request, "cpc_dashboard.html")

