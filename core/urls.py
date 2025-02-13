from django.urls import path
from .views import *

urlpatterns = [
    path("", home_view, name="home"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_user, name="login_user"),
    path("business/", business_dashboard, name="business_dashboard"),
    path("cpc/", cpc_dashboard, name="cpc_dashboard"),
]
