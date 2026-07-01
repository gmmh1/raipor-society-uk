from django.contrib import admin

from apps.shop.models import Product, ShopOrder, ShopOrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "sku", "name", "price_minor", "currency", "inventory_count", "is_active")
    list_filter = ("is_active", "currency")
    search_fields = ("sku", "name")


class ShopOrderItemInline(admin.TabularInline):
    model = ShopOrderItem
    extra = 0


@admin.register(ShopOrder)
class ShopOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_minor", "currency", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("user__username", "user__email")
    inlines = [ShopOrderItemInline]
