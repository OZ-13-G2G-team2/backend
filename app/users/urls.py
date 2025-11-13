from django.urls import path
from .views import (
    UserDetailView,
    ChangePasswordView,
    UserList,
)

app_name = "users"

urlpatterns = [
    # --- 관리/조회 ---
    path("list/", UserList.as_view(), name="user-list"),  # 전체 유저 조회
    # --- 유저 정보 ---
    path("<int:id>/", UserDetailView.as_view(), name="user-detail"),  # 상세 조회
    path("password/change/", ChangePasswordView.as_view(), name="change-password"),
]
