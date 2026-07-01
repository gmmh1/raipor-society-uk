from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.permissions import HasAnyRole
from apps.shop.application.order_service import ShopError, create_order_for_user, transition_order_status
from apps.shop.models import Product, ShopOrder
from apps.shop.presentation.serializers import (
    OrderCreateSerializer,
    OrderTransitionSerializer,
    ProductSerializer,
    ShopOrderSerializer,
)


class ProductListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            self.required_roles = ("admin", "volunteer")
            return [IsAuthenticated(), HasAnyRole()]
        return [AllowAny()]

    def get(self, _request):
        products = Product.objects.filter(is_active=True).order_by("name")
        return Response(ProductSerializer(products, many=True).data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = create_order_for_user(user=request.user, items=serializer.validated_data["items"])
        except ShopError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ShopOrderSerializer(order).data, status=status.HTTP_201_CREATED)


class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = ShopOrder.objects.filter(user=request.user).prefetch_related("items", "items__product")
        return Response(ShopOrderSerializer(orders, many=True).data)


class OrderTransitionView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "volunteer", "treasurer")

    def post(self, request):
        serializer = OrderTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = ShopOrder.objects.get(id=serializer.validated_data["order_id"])
        except ShopOrder.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            updated = transition_order_status(order=order, to_status=serializer.validated_data["to_status"])
        except ShopError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ShopOrderSerializer(updated).data)
