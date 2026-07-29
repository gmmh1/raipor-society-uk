from celery import shared_task

from apps.shop.application.order_service import cancel_stale_pending_orders


@shared_task
def cancel_stale_pending_orders_task() -> int:
    return cancel_stale_pending_orders()
