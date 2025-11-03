from django.contrib import admin
from .models import Product, Category, CategoryGroup

@admin.register(Product)
class ProductSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'origin', 'price', 'stock', 'sold_out')
    search_fields = ('name', 'seller__user__username', 'origin')
    list_filter = ('sold_out', 'categories')

class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


@admin.register(CategoryGroup)
class CategoryGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    inlines = [CategoryInline]
    ordering = ("id",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "group")
    list_filter = ("group",)
    ordering = ("id", "group")


