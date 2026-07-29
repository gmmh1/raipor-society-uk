import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.finance.application.payment_service import process_webhook
from apps.finance.models import PaymentTransaction
from apps.identity.models import Role, User
from apps.shop.application.order_service import cancel_stale_pending_orders
from apps.shop.models import Product, ShopOrder
from apps.shop.tasks import cancel_stale_pending_orders_task


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


@pytest.mark.django_db
def test_deactivate_product_soft_deletes_and_preserves_order_history():
    admin = User.objects.create_user(username="shop-admin-1", password="pass123")
    role = Role.objects.create(code="admin", name="Admin")
    admin.roles.add(role)

    customer = User.objects.create_user(username="shop-user-4", password="pass123")
    product = Product.objects.create(
        name="Retiring Item", sku="SKU-RETIRE", price_minor=500, inventory_count=5, is_active=True
    )

    client = APIClient()
    client.force_authenticate(user=customer)
    order_response = client.post(
        reverse("shop-orders-create"),
        data={"items": [{"product_id": str(product.id), "quantity": 1}]},
        format="json",
    )
    assert order_response.status_code == 201

    client.force_authenticate(user=admin)
    deactivate_response = client.post(
        reverse("shop-products-deactivate", kwargs={"product_id": product.id})
    )
    assert deactivate_response.status_code == 204

    assert Product.objects.filter(id=product.id).count() == 0
    soft_deleted = Product.all_objects.get(id=product.id)
    assert soft_deleted.deleted_at is not None
    assert soft_deleted.is_active is False

    listing = client.get(reverse("shop-products-list-create"))
    assert all(item["sku"] != "SKU-RETIRE" for item in listing.json())

    client.force_authenticate(user=customer)
    order_response = client.get(reverse("shop-orders-me"))
    assert order_response.json()[0]["items"][0]["product_id"] == str(product.id)


@pytest.mark.django_db
def test_deactivate_product_requires_role():
    user = User.objects.create_user(username="shop-user-5", password="pass123")
    product = Product.objects.create(
        name="Item", sku="SKU-PROTECTED", price_minor=100, inventory_count=1, is_active=True
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(reverse("shop-products-deactivate", kwargs={"product_id": product.id}))

    assert response.status_code == 403
    assert Product.objects.filter(id=product.id).count() == 1


@pytest.mark.django_db
def test_cancelling_order_restores_inventory():
    customer = User.objects.create_user(username="shop-user-6", password="pass123")
    admin = User.objects.create_user(username="shop-admin-2", password="pass123")
    role = Role.objects.create(code="admin", name="Admin")
    admin.roles.add(role)

    product = Product.objects.create(
        name="Item", sku="SKU-CANCEL", price_minor=500, inventory_count=5, is_active=True
    )

    client = APIClient()
    client.force_authenticate(user=customer)
    order_response = client.post(
        reverse("shop-orders-create"),
        data={"items": [{"product_id": str(product.id), "quantity": 3}]},
        format="json",
    )
    order_id = order_response.json()["id"]
    product.refresh_from_db()
    assert product.inventory_count == 2

    client.force_authenticate(user=admin)
    cancel_response = client.post(
        reverse("shop-orders-transition"),
        data={"order_id": order_id, "to_status": "cancelled"},
        format="json",
    )
    assert cancel_response.status_code == 200
    product.refresh_from_db()
    assert product.inventory_count == 5


@pytest.mark.django_db
def test_checkout_endpoint_initiates_payment(monkeypatch):
    monkeypatch.setattr(
        "apps.finance.application.payment_service.create_stripe_checkout_session",
        lambda **kwargs: {"external_id": "cs_shop_1", "redirect_url": "https://stripe.example/pay"},
    )

    customer = User.objects.create_user(username="shop-user-7", password="pass123")
    product = Product.objects.create(
        name="Item", sku="SKU-CHECKOUT", price_minor=1000, inventory_count=5, is_active=True
    )

    client = APIClient()
    client.force_authenticate(user=customer)
    order_response = client.post(
        reverse("shop-orders-create"),
        data={"items": [{"product_id": str(product.id), "quantity": 1}]},
        format="json",
    )
    order_id = order_response.json()["id"]

    checkout_response = client.post(
        reverse("shop-orders-checkout", kwargs={"order_id": order_id}),
        data={
            "provider": "stripe",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
        },
        format="json",
    )

    assert checkout_response.status_code == 201
    assert checkout_response.json()["redirect_url"] == "https://stripe.example/pay"
    tx = PaymentTransaction.objects.get(external_id="cs_shop_1")
    assert tx.payload["entry_type"] == "shop_sale"

    order = ShopOrder.objects.get(id=order_id)
    assert tx.payload["reference"] == str(order.payment_reference)


@pytest.mark.django_db
def test_checkout_endpoint_rejects_other_users_order():
    owner = User.objects.create_user(username="shop-user-8", password="pass123")
    stranger = User.objects.create_user(username="shop-user-9", password="pass123")
    order = ShopOrder.objects.create(user=owner, status="pending", total_minor=500, currency="GBP")

    client = APIClient()
    client.force_authenticate(user=stranger)
    response = client.post(
        reverse("shop-orders-checkout", kwargs={"order_id": order.id}),
        data={
            "provider": "stripe",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
        },
        format="json",
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_stripe_webhook_marks_shop_order_paid():
    customer = User.objects.create_user(username="shop-user-10", password="pass123")
    order = ShopOrder.objects.create(
        user=customer, status="pending", total_minor=5000, currency="GBP"
    )
    PaymentTransaction.objects.create(
        provider="stripe",
        external_id="cs_shop_paid_1",
        status="pending",
        amount_minor=5000,
        currency="GBP",
        payer=customer,
        payload={
            "entry_type": "shop_sale",
            "description": f"Shop order {order.id}",
            "reference": str(order.payment_reference),
        },
    )

    payload = {
        "id": "evt_shop_1",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_shop_paid_1",
                "amount_total": 5000,
                "currency": "gbp",
                "status": "complete",
            }
        },
    }
    process_webhook(provider="stripe", payload=payload)

    order.refresh_from_db()
    assert order.status == "paid"


@pytest.mark.django_db
def test_cancel_stale_pending_orders_releases_inventory_and_cancels():
    customer = User.objects.create_user(username="shop-user-11", password="pass123")
    product = Product.objects.create(
        name="Item", sku="SKU-STALE", price_minor=500, inventory_count=5, is_active=True
    )
    order = ShopOrder.objects.create(
        user=customer, status="pending", total_minor=1000, currency="GBP"
    )
    from apps.shop.models import ShopOrderItem

    ShopOrderItem.objects.create(
        order=order, product=product, quantity=2, unit_price_minor=500, line_total_minor=1000
    )
    product.inventory_count = 3
    product.save(update_fields=["inventory_count"])

    stale_time = timezone.now() - timezone.timedelta(minutes=45)
    ShopOrder.objects.filter(id=order.id).update(created_at=stale_time)

    count = cancel_stale_pending_orders()

    assert count == 1
    order.refresh_from_db()
    product.refresh_from_db()
    assert order.status == "cancelled"
    assert product.inventory_count == 5


@pytest.mark.django_db
def test_cancel_stale_pending_orders_task_delegates_to_service():
    customer = User.objects.create_user(username="shop-user-12", password="pass123")
    ShopOrder.objects.create(user=customer, status="pending", total_minor=100, currency="GBP")

    assert cancel_stale_pending_orders_task() == 0


@pytest.mark.django_db
def test_admin_order_list_requires_role_and_returns_all_orders():
    customer_a = User.objects.create_user(username="shop-user-13", password="pass123")
    customer_b = User.objects.create_user(username="shop-user-14", password="pass123")
    ShopOrder.objects.create(user=customer_a, status="pending", total_minor=500, currency="GBP")
    ShopOrder.objects.create(user=customer_b, status="paid", total_minor=750, currency="GBP")

    client = APIClient()
    client.force_authenticate(user=customer_a)
    forbidden = client.get(reverse("shop-orders-admin-list"))
    assert forbidden.status_code == 403

    role = Role.objects.create(code="admin", name="Admin")
    customer_a.roles.add(role)
    allowed = client.get(reverse("shop-orders-admin-list"))
    assert allowed.status_code == 200
    assert allowed.json()["count"] == 2

    filtered = client.get(reverse("shop-orders-admin-list"), {"status": "paid"})
    assert filtered.json()["count"] == 1
    assert filtered.json()["results"][0]["username"] == "shop-user-14"
