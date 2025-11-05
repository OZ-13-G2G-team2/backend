from django.db import models
from users.models import User
from products.models import Product

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlists")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-created_at"]
        verbose_name = "위시리스트"
        verbose_name_plural = "위시리스트 목록"

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    # ✅ 추가 기능들
    def toggle(self):
        """활성화 상태 토글"""
        self.is_active = not self.is_active
        self.save()
        return self.is_active

    @classmethod
    def active_count(cls):
        """활성화된 찜 개수 반환"""
        return cls.objects.filter(is_active=True).count()

    @classmethod
    def user_wishlist(cls, user):
        """특정 유저의 찜 목록 반환"""
        return cls.objects.filter(user=user, is_active=True).select_related("product")

    @classmethod
    def product_wishlist_count(cls, product):
        """특정 상품의 찜 수 반환"""
        return cls.objects.filter(product=product, is_active=True).count()

