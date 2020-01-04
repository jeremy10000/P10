from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .forms import LoginForm


"""
    for templates
    login:<name>

"""
app_name = 'login'

urlpatterns = [
    path('', LoginView.as_view(authentication_form=LoginForm), name="connect"),
    path('logout/', LogoutView.as_view(), name="disconnect"),
    path('join/', views.Join.as_view(), name="join"),
    path('mypage/', views.mypage, name="mypage"),
]
