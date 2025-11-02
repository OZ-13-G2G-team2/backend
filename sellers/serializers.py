from rest_framework import serializers
from sellers.models import Seller


class SellersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'
        read_only_fields = ('id',)