from django.contrib import admin
from .models import Product, Category, CategoryGroup

admin.site.register(Product)

class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0

@admin.register(CategoryGroup)
class CategoryGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    inlines = [CategoryInline]
    ordering = ('id',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group')
    list_filter = ('group',)
    ordering = ('id', 'group')