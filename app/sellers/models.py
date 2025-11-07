from django.db import models
from app.users.models import User


class Seller(models.Model):
    id = models.BigAutoField(primary_key=True)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="seller_profile",
    )

    business_address = models.CharField(max_length=100, null=True, blank=True)
    business_name = models.CharField(max_length=225)
    business_number = models.CharField(max_length=100)

    class Meta:
        db_table = "sellers"

    def __str__(self):
        return f"{self.business_name} ({self.user.username})"
