from django.urls import path
from .views import (
    ReviewCreateView,
    ReviewListView,
    ReviewUpdateView,
    ReviewDeleteView,
    ReviewLikeView,
    ReviewImageUploadView,
)

urlpatterns = [
    path("", ReviewCreateView.as_view(), name="review-create"),  # POST
    path("", ReviewListView.as_view(), name="review-list"),  # GET ?product_id=
    path("<int:pk>/", ReviewUpdateView.as_view(), name="review-update"),  # PUT
    path("<int:pk>/", ReviewDeleteView.as_view(), name="review-delete"),  # DELETE
    path("<int:review_id>/like/", ReviewLikeView.as_view(), name="review-like"),  # POST
    path(
        "<int:review_id>/image/", ReviewImageUploadView.as_view(), name="review-image"
    ),  # POST
]
