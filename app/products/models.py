from django.db import models
from app.sellers.models import Seller
from app.users.models import User


class CategoryGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "카테고리 그룹"
        verbose_name_plural = "카테고리 그룹들"
        ordering = ["name"]


class Category(models.Model):
    name = models.CharField(max_length=50)
    group = models.ForeignKey(
        CategoryGroup, on_delete=models.CASCADE, related_name="categories"
    )

    def __str__(self):
        return f"{self.group.name} - {self.name}"

    class Meta:
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리들"
        ordering = ["group__name", "name"]
        unique_together = ("name", "group")


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(
        Seller, verbose_name="판매자", on_delete=models.CASCADE
    )
    categories = models.ManyToManyField(
        "Category", verbose_name="카테고리", related_name="products", blank=True
    )
    name = models.CharField(verbose_name="상품명", max_length=255, null=False)
    origin = models.CharField(verbose_name="원산지", max_length=100)
    stock = models.PositiveIntegerField(default=0, verbose_name="재고")
    price = models.DecimalField(
        verbose_name="가격", max_digits=10, decimal_places=2, null=False
    )
    discount_price = models.DecimalField(
        verbose_name="할인 가격", max_digits=10, decimal_places=2, default=0, null=True
    )
    overseas_shipping = models.BooleanField(verbose_name="해외배송 여부", default=False)
    delivery_fee = models.DecimalField(
        verbose_name="배송비", max_digits=10, decimal_places=2, default=0
    )
    description = models.TextField(verbose_name="상품설명")
    sold_out = models.BooleanField(verbose_name="품절버튼", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        seller_user = self.seller
        if hasattr(self.seller, "user"):
            seller_user = self.seller.user
        return f"{self.name} - {seller_user.username} - {self.origin}"

    class Meta:
        verbose_name = "상품"
        verbose_name_plural = "상품들"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["seller_id"]),
        ]

    def save(self, *args, update_sold_out=True, **kwargs):
        if update_sold_out:
            self.sold_out = self.stock == 0
        super().save(*args, **kwargs)


class ProductStats(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="stats")
    review_count = models.PositiveIntegerField(verbose_name="리뷰 수", default=0)
    sales_count = models.PositiveIntegerField(verbose_name="판매 수", default=0)
    wish_count = models.PositiveIntegerField(verbose_name="위시 수", default=0)

    class Meta:
        verbose_name = "상품 통계"
        verbose_name_plural = "상품 통계들"
        ordering = ["-sales_count", "-review_count"]
        indexes = [
            models.Index(fields=["sales_count"]),
            models.Index(fields=["review_count"]),
            models.Index(fields=["wish_count"]),
        ]
    def __str__(self):
        return f"{self.product.name} 통계 (판매 {self.sales_count}회)"


class ProductImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="images"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, default=1
    )
    image_url = models.ImageField(upload_to="product_images/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"

    class Meta:
        verbose_name = "상품 이미지"
        verbose_name_plural = "상품 이미지들"
        ordering = ["product_id", "image_id"]


# upload_to='product_images/' MEDIA_ROOT 내부 경로로 저장
# 배포 서버에서도 동일하게 MEDIA_ROOT 하위 경로로 저장됨


class ProductOptionValue(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="option_values",
        verbose_name="상품",
    )
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, verbose_name="옵션 카테고리"
    )
    extra_price = models.DecimalField(
        verbose_name="추가 금액", max_digits=10, decimal_places=2, default=0
    )

    def __str__(self):
        return f"{self.product.name} - {self.category.name}"

    class Meta:
        verbose_name = "상품 옵션 값"
        verbose_name_plural = "상품 옵션 값들"
        ordering = ["product", "category"]
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["category"]),
        ]
