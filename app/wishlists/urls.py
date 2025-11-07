from django.urls import path
from .views import WishlistView, WishlistDeleteView, WishlistToggleView

app_name = "app.wishlists"

urlpatterns = [
    path("", WishlistView.as_view(), name="wishlist"),
    path("<int:wish_id>/", WishlistDeleteView.as_view(), name="wishlist-delete"),
    path("<int:wish_id>/toggle", WishlistToggleView.as_view(), name="wishlist-toggle"),
]
