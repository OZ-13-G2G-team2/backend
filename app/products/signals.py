from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from app.products.models import CategoryGroup, Category, Product, ProductStats


@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    if sender.name != "app.products":
        return

    if CategoryGroup.objects.exists():
        return

    g1 = CategoryGroup.objects.create(name="시즌")
    g2 = CategoryGroup.objects.create(name="테마")
    g3 = CategoryGroup.objects.create(name="색상")
    g4 = CategoryGroup.objects.create(name="사이즈")
    g5 = CategoryGroup.objects.create(name="kg")

    Category.objects.bulk_create(
        [
            Category(name="봄", group=g1),
            Category(name="여름", group=g1),
            Category(name="가을", group=g1),
            Category(name="겨울", group=g1),
            Category(name="식량/작물", group=g2),
            Category(name="채소류", group=g2),
            Category(name="과채류", group=g2),
            Category(name="과실류", group=g2),
            Category(name="축산물", group=g2),
            Category(name="특작류", group=g2),
            Category(name="화훼류", group=g2),
            Category(name="농산가공", group=g2),
            Category(name="장류", group=g2),
            Category(name="기타", group=g2),
            Category(name="빨강", group=g3),
            Category(name="노랑", group=g3),
            Category(name="초록", group=g3),
            Category(name="파랑", group=g3),
            Category(name="검정", group=g3),
            Category(name="소", group=g4),
            Category(name="중", group=g4),
            Category(name="대", group=g4),
            Category(name="특대", group=g4),
            Category(name="500g", group=g5),
            Category(name="1kg", group=g5),
            Category(name="2kg", group=g5),
            Category(name="3kg", group=g5),
            Category(name="4kg", group=g5),
            Category(name="5kg", group=g5),
            Category(name="7kg", group=g5),
            Category(name="10kg", group=g5),
            Category(name="20kg", group=g5),
        ]
    )


@receiver(post_save, sender=Product)
def crate_product_stats(sender, instance, created, **kwargs):
    if created:
        ProductStats.objects.create(product=instance)
