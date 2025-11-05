from django.contrib import admin
from django.utils.html import format_html
from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "product_thumbnail",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("user__username", "product__name")
    ordering = ("-created_at",)
    actions = ["activate_wishlist", "deactivate_wishlist"]

    def product_thumbnail(self, obj):
        """ProductImages 중 첫 번째 이미지를 표시"""
        first_image = obj.product.images.first()
        if first_image and first_image.image_url:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:4px;" />',
                first_image.image_url.url,
            )
        return "(이미지 없음)"
    product_thumbnail.short_description = "상품 이미지"

    def activate_wishlist(self, request, queryset):
        queryset.update(is_active=True)
    activate_wishlist.short_description = "선택된 찜 활성화"

    def deactivate_wishlist(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_wishlist.short_description = "선택된 찜 비활성화"

