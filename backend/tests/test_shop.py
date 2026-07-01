import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.identity.models import Role, User
from apps.shop.models import Product, ShopOrder


@pytest.mark.django_db
def test_public_products_only_show_active():
    Product.objects.create(name="A", sku="SKU-A", price_minor=100, inventory_count=5, is_active=True)
    Product.objects.create(name="B", sku="SKU-B", price_minor=100, inventory_count=5, is_active=False)

    client = APIClient()
    response = client.get(reverse("shop-products-list-create"))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["sku"] == "SKU-A"


@pytest.mark.django_db
def test_product_create_requires_role():
    user = User.objects.create_user(username="shop-user-1", password="pass123")
    client = APIClient()
    client.force_authenticate(user=user)

    forbidden = client.post(
        reverse("shop-products-list-create"),
        data={"name": "Item", "sku": "SKU-NEW", "price_minor": 500, "inventory_count": 2, "is_active": True},
        format="json",
    )
    assert forbidden.status_code == 403

    role = Role.objects.create(code="volunteer", name="Volunteer")
    user.roles.add(role)

    allowed = client.post(
        reverse("shop-products-list-create"),
        data={"name": "Item", "sku": "SKU-NEW", "price_minor": 500, "inventory_count": 2, "is_active": True},
        format="json",
    )
    assert allowed.status_code == 201


@pytest.mark.django_db
def test_order_create_decrements_inventory():
    user = User.objects.create_user(username="shop-user-2", password="pass123")
    product = Product.objects.create(name="Item", sku="SKU-1", price_minor=750, inventory_count=3, is_active=True)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        reverse("shop-orders-create"),
        data={"items": [{"product_id": str(product.id), "quantity": 2}]},
        format="json",
    )

    assert response.status_code == 201
    product.refresh_from_db()
    assert product.inventory_count == 1


@pytest.mark.django_db
def test_order_transition_role_gate_and_valid_transition():
    customer = User.objects.create_user(username="shop-user-3", password="pass123")
    ops = User.objects.create_user(username="shop-ops", password="pass123")
    product = Product.objects.create(name="Item", sku="SKU-2", price_minor=500, inventory_count=10, is_active=True)

    order = ShopOrder.objects.create(user=customer, status="pending", total_minor=500, currency="GBP")

    client = APIClient()
    client.force_authenticate(user=ops)
    forbidden = client.post(
        reverse("shop-orders-transition"),
        data={"order_id": str(order.id), "to_status": "paid"},
        format="json",
    )
    assert forbidden.status_code == 403

    role = Role.objects.create(code="treasurer", name="Treasurer")
    ops.roles.add(role)

    allowed = client.post(
        reverse("shop-orders-transition"),
        data={"order_id": str(order.id), "to_status": "paid"},
        format="json",
    )
    assert allowed.status_code == 200
    order.refresh_from_db()
    assert order.status == "paid"
