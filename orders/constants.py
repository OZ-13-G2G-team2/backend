

STATUS_PENDING = 'pending'
STATUS_COMPLETED = 'completed'
STATUS_CANCELLED = 'cancelled'
STATUS_SHIPPING = 'shipping'
STATUS_DELIVERED = 'delivered'

STATUS_CHOICES = [
    (STATUS_PENDING, '결제 대기'),
    (STATUS_COMPLETED, '결제 완료'),
    (STATUS_CANCELLED, '결제 취소'),
    (STATUS_SHIPPING, '배송 중'),
    (STATUS_DELIVERED, '배달 완료'),
]
