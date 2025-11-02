from django.urls import path
from .views import UserRegisterView, UserLoginView, UserTokenRefreshView, UserDetailView, SellerRegisterView

app_name = "users"

urlpatterns = [
    path('signup/', UserRegisterView.as_view(), name='user-signup'),
    path('signup/seller', SellerRegisterView.as_view(), name='seller-signup'),
    path('login/', UserLoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', UserTokenRefreshView.as_view(), name='token_refresh'),
    path('<int:id>/', UserDetailView.as_view(), name='user-detail'),
]
