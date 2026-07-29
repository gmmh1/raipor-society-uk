from django.db import transaction
from django.utils import timezone

from apps.documents.infrastructure import storage
from apps.finance.infrastructure.pdf import render_receipt_pdf
from apps.finance.models import LedgerEntry, Receipt


class ReceiptError(ValueError):
    pass


def _next_receipt_number(receipt_id) -> str:
    # Derived from the row's own UUID rather than a sequential counter — simple and
    # collision-free without a locked counter table. Not suitable as a VAT invoice
    # number; see ADR 0014's Future considerations if the charity becomes
    # VAT-registered.
    today = timezone.localdate()
    return f"RCT-{today:%Y%m%d}-{str(receipt_id)[:8].upper()}"


@transaction.atomic
def issue_receipt(*, ledger_entry: LedgerEntry, recipient, actor) -> Receipt:
    if Receipt.objects.filter(ledger_entry=ledger_entry).exists():
        raise ReceiptError("A receipt has already been issued for this ledger entry.")

    receipt = Receipt.objects.create(
        ledger_entry=ledger_entry,
        recipient=recipient,
        receipt_number="",
        amount_minor=ledger_entry.amount_minor,
        currency=ledger_entry.currency,
        description=ledger_entry.description,
        pdf_file_key="",
        issued_by=actor,
    )
    receipt.receipt_number = _next_receipt_number(receipt.id)

    recipient_name = recipient.get_full_name() or recipient.username if recipient else "Supporter"
    amount_display = f"{receipt.currency} {receipt.amount_minor / 100:.2f}"
    pdf_bytes = render_receipt_pdf(
        context={
            "receipt_number": receipt.receipt_number,
            "issued_at": receipt.created_at.strftime("%d %B %Y"),
            "recipient_name": recipient_name,
            "description": receipt.description or "Payment",
            "amount_display": amount_display,
        }
    )

    file_key = f"receipts/{receipt.receipt_number}.pdf"
    storage.upload_bytes(key=file_key, data=pdf_bytes, content_type="application/pdf")
    receipt.pdf_file_key = file_key
    receipt.save(update_fields=["receipt_number", "pdf_file_key"])
    return receipt


def get_receipt_download_url(*, receipt: Receipt) -> str:
    return storage.generate_presigned_download_url(key=receipt.pdf_file_key)
