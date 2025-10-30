from django.db import models

class CategoryGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50)
    group = models.ForeignKey(
        CategoryGroup,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    def __str__(self):
        return f"{self.group.name} - {self.name}"


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    seller_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    categories = models.ManyToManyField(
        'Category',
        related_name='products',
        blank=True
    )
    name = models.CharField(max_length=255, not_null=True)
    origin = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, not_null=True)
    overseas_shipping = models.BooleanField(default=False)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    sold_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProductImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    image_url = models.URLField(not_null=True)
    created_at = models.DateTimeField(auto_now_add=True)


