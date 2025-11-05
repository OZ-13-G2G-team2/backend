# Register your models here.
from django.contrib import admin
from .models import Seller

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("id", "user_email", "business_name", "business_number", "business_address")
    search_fields = ("user__email", "business_name", "business_number")
    list_filter = ("business_name",)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"