from django.contrib import admin
from .models import Order
from .models import OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'total_amount', 'status', 'payment_method')
    list_filter = ('status', 'payment_method', 'order_date')
    search_fields = ('user__username', 'address', 'id')
    readonly_fields = ('created_at', 'updated_at', 'order_date')
    ordering = ('-order_date',)
    list_per_page = 20

    @admin.register(OrderItem)
    class OrderItemAdmin(admin.ModelAdmin):
        list_display = ('id', 'order', 'product', 'quantity', 'price_at_purchase', 'subtotal')
        search_fields = ('order__id', 'product__name')
