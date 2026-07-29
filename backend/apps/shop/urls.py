from django.urls import path

from apps.shop.presentation.views import (
    MyOrdersView,
    OrderCheckoutView,
    OrderCreateView,
    OrderTransitionView,
    ProductDeactivateView,
    ProductListCreateView,
)

urlpatterns = [
    path("products/", ProductListCreateView.as_view(), name="shop-products-list-create"),
    path(
        "products/<uuid:product_id>/deactivate/",
        ProductDeactivateView.as_view(),
        name="shop-products-deactivate",
    ),
    path("orders/", OrderCreateView.as_view(), name="shop-orders-create"),
    path("orders/me/", MyOrdersView.as_view(), name="shop-orders-me"),
    path(
        "orders/<uuid:order_id>/checkout/",
        OrderCheckoutView.as_view(),
        name="shop-orders-checkout",
    ),
    path("orders/transitions/", OrderTransitionView.as_view(), name="shop-orders-transition"),
]
