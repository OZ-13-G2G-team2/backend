from django.urls import path
from .views import UserRegisterView, UserDetailView


app_name = "users"

urlpatterns = [
    # path('register/', UserRegisterView.as_view(), name='register'),
]
