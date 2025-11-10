from django.db import models
from app.users.models import User


class Seller(models.Model):
    id = models.BigAutoField(primary_key=True)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="seller_profile",
    )

    business_address = models.CharField(max_length=225, null=True, blank=True)
    business_name = models.CharField(max_length=225, verbose_name="업체명(상호명)")
    business_number = models.CharField(
        max_length=100, verbose_name="사업자등록번호", unique=True
    )

    class Meta:
        db_table = "sellers"
        verbose_name_plural = "판매자 정보"

    def __str__(self):
        return f"{self.business_name} ({self.user.username})"
