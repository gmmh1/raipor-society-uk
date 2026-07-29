from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import StandardResultsPagination
from apps.identity.permissions import HasAnyRole
from apps.shop.application.order_service import (
    ShopError,
    create_order_for_user,
    deactivate_product,
    initiate_order_checkout,
    transition_order_status,
)
from apps.shop.domain.types import ORDER_STATUS_CHOICES
from apps.shop.models import Product, ShopOrder
from apps.shop.presentation.serializers import (
    AdminShopOrderSerializer,
    OrderCheckoutRequestSerializer,
    OrderCheckoutSerializer,
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


class ProductDeactivateView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "volunteer")

    def post(self, _request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        deactivate_product(product=product)
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class OrderCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = ShopOrder.objects.get(id=order_id, user=request.user)
        except ShopOrder.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderCheckoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = initiate_order_checkout(
                order=order,
                provider=serializer.validated_data["provider"],
                payer=request.user,
                success_url=serializer.validated_data["success_url"],
                cancel_url=serializer.validated_data["cancel_url"],
            )
        except ShopError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderCheckoutSerializer(result).data, status=status.HTTP_201_CREATED)


class AdminOrderListView(APIView):
    """All orders across all members, for order fulfilment/administration —
    distinct from ``MyOrdersView``, which is scoped to the requesting user."""

    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "volunteer", "treasurer")

    def get(self, request):
        valid_statuses = {choice[0] for choice in ORDER_STATUS_CHOICES}
        status_filter = request.query_params.get("status", "").strip()

        orders = ShopOrder.objects.select_related("user").prefetch_related(
            "items", "items__product"
        ).order_by("-created_at")
        if status_filter:
            if status_filter not in valid_statuses:
                return Response(
                    {"detail": f"Unknown status '{status_filter}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            orders = orders.filter(status=status_filter)

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(orders, request)
        serializer = AdminShopOrderSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


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
