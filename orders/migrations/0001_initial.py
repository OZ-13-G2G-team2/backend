from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("products", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "order_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="주문일"),
                ),
                (
                    "total_amount",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="총 금액"
                    ),
                ),
                ("address", models.CharField(default="", max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "결제 대기"),
                            ("completed", "결제 완료"),
                            ("cancelled", "결제 취소"),
                            ("shipping", "배송 중"),
                            ("delivered", "배달 완료"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="주문 상태",
                    ),
                ),
                (
                    "payment_method",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="결제 방법"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성일"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="수정일"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="주문자",
                    ),
                ),
            ],
            options={
                "verbose_name": "주문",
                "verbose_name_plural": "주문 목록",
                "db_table": "orders",
                "ordering": ["-order_date"],
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(verbose_name="수량")),
                (
                    "price_at_purchase",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="구매 당시 가격"
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="orders.Order",
                        related_name="items",
                        verbose_name="주문",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.Product",
                        verbose_name="상품",
                    ),
                ),
            ],
            options={
                "verbose_name": "주문 상세",
                "verbose_name_plural": "주문 상세 목록",
                "db_table": "order_items",
                "ordering": ["order"],
            },
        ),
    ]
