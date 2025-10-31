from django.db import models

class CategoryGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '카테고리 그룹'
        verbose_name_plural = '카테고리 그룹들'
        ordering = ['name']

class Category(models.Model):
    name = models.CharField(max_length=50)
    group = models.ForeignKey(
        CategoryGroup,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    def __str__(self):
        return f"{self.group.name} - {self.name}"

    class Meta:
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리들'
        ordering = ['group__name', 'name']
        unique_together = ('name', 'group')


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    seller_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    categories = models.ManyToManyField(
        'Category',
        related_name='products',
        blank=True
    )
    name = models.CharField(max_length=255, null=False)
    origin = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    overseas_shipping = models.BooleanField(default=False)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    sold_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '상품'
        verbose_name_plural = '상품들'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['seller_id']),
        ]

class ProductImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    image_url = models.URLField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '상품 이미지'
        verbose_name_plural = '상품 이미지들'
        ordering = ['product_id', 'image_id']

class ProductOptions(models.Model):
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.product_id.name} - {self.name}"

    class Meta:
        verbose_name = '상품 옵션'
        verbose_name_plural = '상품 옵션들'
        ordering = ['product_id', 'name']

class ProductOptionValue(models.Model):
    option = models.ForeignKey('ProductOptions', on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=50)
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.option.name} - {self.value}"

    class Meta:
        verbose_name = '옵션 값'
        verbose_name_plural = '옵션 값들'
        ordering = ['option', 'value']

