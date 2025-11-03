from django.conf import settings
from users.models import User
from django.db import models




class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '결제 대기'),
        ('completed', '결제 완료'),
        ('cancelled', '결제 취소'),
        ('shipping', '배송 중'),
        ('delivered', '배달 완료'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name='주문자')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='주문일')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='총 금액')
    address = models.CharField(max_length=255, default="", null=False, blank=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='주문 상태')
    payment_method = models.CharField(max_length=50, null=True, blank=True, verbose_name='결제 방법')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'orders'
        verbose_name = '주문'
        verbose_name_plural = '주문 목록'
        ordering = ['-order_date']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} ({self.status})"

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])
        return self.total_amount

    def cancel_if_pending_too_long(self, hours=24):
        from django.utils import timezone
        if self.status == 'pending' and (timezone.now() - self.order_date).total_seconds() > hours*3600:
            self.status = 'cancelled'
            self.save(update_fields=['status'])
            return True
        return False

    def mark_shipping(self):
        if self.status == 'completed':
            self.status = 'shipping'
            self.save(update_fields=['status'])

    def mark_delivered(self):
        if self.status == 'shipping':
            self.status = 'delivered'
            self.save(update_fields=['status'])

    @property
    def item_count(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

