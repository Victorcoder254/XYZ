from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .models import User
from .decorators import role_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import User


def home_view(request):
    return render(request, "home.html")

def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        role = request.POST["role"]  # Capturing role from the form

        if role not in ["business_admin", "cpc_admin"]:
            return render(request, "files/signup.html", {"error": "Invalid role selected"})

        user = User.objects.create_user(username=username, email=email, password=password, role=role)
        login(request, user)

        # Redirect based on role
        if role == "business_admin":
            return redirect("business_dashboard")
        else:
            return redirect("cpc_dashboard")

    return render(request, "files/signup.html")


def login_view(request):
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
    return render(request, "login.html")


@login_required
@role_required("business_admin")
def business_dashboard(request):
    return render(request, "business_dashboard.html")

@login_required
@role_required("cpc_admin")
def cpc_dashboard(request):
    return render(request, "cpc_dashboard.html")

