from rest_framework import serializers

from apps.shop.domain.types import ORDER_STATUS_CHOICES
from apps.shop.models import Product, ShopOrder, ShopOrderItem


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "sku",
            "price_minor",
            "currency",
            "inventory_count",
            "is_active",
            "created_at",
            "updated_at",
        ]


class OrderItemRequestSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemRequestSerializer(many=True, allow_empty=False)


class ShopOrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source="product.id", read_only=True)

    class Meta:
        model = ShopOrderItem
        fields = ["id", "product_id", "quantity", "unit_price_minor", "line_total_minor"]


class ShopOrderSerializer(serializers.ModelSerializer):
    items = ShopOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = ShopOrder
        fields = [
            "id",
            "status",
            "total_minor",
            "currency",
            "items",
            "created_at",
            "updated_at",
        ]


class AdminShopOrderSerializer(ShopOrderSerializer):
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta(ShopOrderSerializer.Meta):
        fields = [*ShopOrderSerializer.Meta.fields, "user_id", "username"]


class OrderTransitionSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    to_status = serializers.ChoiceField(choices=[choice[0] for choice in ORDER_STATUS_CHOICES])


class OrderCheckoutRequestSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=["stripe", "paypal"])
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()


class OrderCheckoutSerializer(serializers.Serializer):
    provider = serializers.CharField()
    external_id = serializers.CharField()
    redirect_url = serializers.CharField()
