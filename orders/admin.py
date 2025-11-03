from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price_at_purchase', 'subtotal')
    can_delete = True

    def subtotal(self, obj):
        return obj.quantity * obj.price_at_purchase
    subtotal.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "order_date",
        "total_amount",
        "status",
        "payment_method",
    )
    list_filter = ("status", "payment_method", "order_date")
    search_fields = ("user__username", "address", "id")
    readonly_fields = ("created_at", "updated_at", "order_date", "total_amount")
    ordering = ("-order_date",)
    list_per_page = 20


    inlines = [OrderItemInline]


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)  # 먼저 obj 저장
        total = sum(item.quantity * item.price_at_purchase for item in obj.orderitem_set.all())
        if obj.total_amount != total:
            obj.total_amount = total
            obj.save(update_fields=['total_amount'])


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('orderitem_set')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price_at_purchase', 'subtotal')
    search_fields = ('order__id', 'product__name')

    readonly_fields = ('subtotal',)

    def subtotal(self, obj):
        return obj.quantity * obj.price_at_purchase
    subtotal.short_description = 'Subtotal'

