from rest_framework import serializers
from app.sellers.models import Seller


class SellersSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Seller
        fields = [
            "business_name",
            "business_number",
            "business_address",
            "email",
            "username",
        ]
        read_only_fields = ("id",)
