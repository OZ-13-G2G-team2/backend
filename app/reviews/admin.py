from django.contrib import admin
from app.reviews.models import Review, ReviewImage


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "like_count", "created_at")
    search_fields = ("user__username", "product__name", "comment")
    list_filter = ("created_at",)


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "image_url")
