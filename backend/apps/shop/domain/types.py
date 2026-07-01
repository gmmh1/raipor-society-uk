ORDER_PENDING = "pending"
ORDER_PAID = "paid"
ORDER_FULFILLED = "fulfilled"
ORDER_CANCELLED = "cancelled"

ORDER_STATUS_CHOICES = (
    (ORDER_PENDING, "Pending"),
    (ORDER_PAID, "Paid"),
    (ORDER_FULFILLED, "Fulfilled"),
    (ORDER_CANCELLED, "Cancelled"),
)
