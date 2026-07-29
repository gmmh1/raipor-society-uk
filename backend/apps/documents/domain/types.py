VISIBILITY_PUBLIC = "public"
VISIBILITY_MEMBER = "member"
VISIBILITY_STAFF = "staff"

VISIBILITY_CHOICES = (
    (VISIBILITY_PUBLIC, "Public"),
    (VISIBILITY_MEMBER, "Member"),
    (VISIBILITY_STAFF, "Staff"),
)

STAFF_ROLES = ("admin", "volunteer", "treasurer")

CATEGORY_GOVERNANCE = "governance"
CATEGORY_POLICY = "policy"
CATEGORY_MINUTES = "minutes"
CATEGORY_FORM = "form"
CATEGORY_OTHER = "other"

CATEGORY_CHOICES = (
    (CATEGORY_GOVERNANCE, "Governance"),
    (CATEGORY_POLICY, "Policy"),
    (CATEGORY_MINUTES, "Minutes"),
    (CATEGORY_FORM, "Form"),
    (CATEGORY_OTHER, "Other"),
)

EXTRACTION_PENDING = "pending"
EXTRACTION_PROCESSING = "processing"
EXTRACTION_COMPLETED = "completed"
EXTRACTION_FAILED = "failed"
EXTRACTION_UNSUPPORTED = "unsupported"

EXTRACTION_STATUS_CHOICES = (
    (EXTRACTION_PENDING, "Pending"),
    (EXTRACTION_PROCESSING, "Processing"),
    (EXTRACTION_COMPLETED, "Completed"),
    (EXTRACTION_FAILED, "Failed"),
    (EXTRACTION_UNSUPPORTED, "Unsupported"),
)
