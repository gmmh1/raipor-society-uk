ENTRY_TYPE_DONATION = "donation"
ENTRY_TYPE_MEMBERSHIP_FEE = "membership_fee"
ENTRY_TYPE_SHOP_SALE = "shop_sale"
ENTRY_TYPE_EXPENSE = "expense"
ENTRY_TYPE_REFUND = "refund"

ENTRY_TYPE_CHOICES = (
    (ENTRY_TYPE_DONATION, "Donation"),
    (ENTRY_TYPE_MEMBERSHIP_FEE, "Membership Fee"),
    (ENTRY_TYPE_SHOP_SALE, "Shop Sale"),
    (ENTRY_TYPE_EXPENSE, "Expense"),
    (ENTRY_TYPE_REFUND, "Refund"),
)

DIRECTION_DEBIT = "debit"
DIRECTION_CREDIT = "credit"
DIRECTION_CHOICES = (
    (DIRECTION_DEBIT, "Debit"),
    (DIRECTION_CREDIT, "Credit"),
)

PROVIDER_STRIPE = "stripe"
PROVIDER_PAYPAL = "paypal"
PROVIDER_MANUAL = "manual"
PROVIDER_CHOICES = (
    (PROVIDER_STRIPE, "Stripe"),
    (PROVIDER_PAYPAL, "PayPal"),
    (PROVIDER_MANUAL, "Manual"),
)

PAYMENT_PENDING = "pending"
PAYMENT_SUCCEEDED = "succeeded"
PAYMENT_FAILED = "failed"
PAYMENT_REFUNDED = "refunded"
PAYMENT_STATUS_CHOICES = (
    (PAYMENT_PENDING, "Pending"),
    (PAYMENT_SUCCEEDED, "Succeeded"),
    (PAYMENT_FAILED, "Failed"),
    (PAYMENT_REFUNDED, "Refunded"),
)
