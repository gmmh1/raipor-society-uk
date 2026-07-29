"""PDF rendering for receipts, via WeasyPrint (open-source, no licensing cost).

WeasyPrint is imported lazily inside the function rather than at module level: it
requires native Pango/Cairo libraries that are only guaranteed present in the
deployed container (see the Dockerfile), not in every environment that merely
imports this module.
"""

from django.template.loader import render_to_string

RECEIPT_TEMPLATE = "finance/receipt.html"


def render_receipt_pdf(*, context: dict) -> bytes:
    from weasyprint import HTML

    html = render_to_string(RECEIPT_TEMPLATE, context)
    return HTML(string=html).write_pdf()
