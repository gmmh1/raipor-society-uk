from django.urls import path

from apps.shop.presentation.views import (
    MyOrdersView,
    OrderCreateView,
    OrderTransitionView,
    ProductListCreateView,
)

urlpatterns = [
    path("products/", ProductListCreateView.as_view(), name="shop-products-list-create"),
    path("orders/", OrderCreateView.as_view(), name="shop-orders-create"),
    path("orders/me/", MyOrdersView.as_view(), name="shop-orders-me"),
    path("orders/transitions/", OrderTransitionView.as_view(), name="shop-orders-transition"),
]
