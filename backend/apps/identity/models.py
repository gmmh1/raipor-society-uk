from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel, UUIDModel

MINOR_AGE_THRESHOLD = 18


class Role(TimeStampedModel):
    # Deliberately keeps its original BigAutoField PK rather than UUIDModel: switching
    # an existing bigint PK to UUID requires a real data migration (regenerate ids,
    # repoint the identity_user_roles FK), which is out of scope for this refactor.
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "identity_role"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.code}: {self.name}"


class User(UUIDModel, TimeStampedModel, AbstractUser):
    roles = models.ManyToManyField(Role, blank=True, related_name="users")
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "identity_user"
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    @property
    def is_minor(self) -> bool:
        """True only when date_of_birth is known and under the UK age of majority.

        Unknown date_of_birth is treated as not-minor (unchanged pre-existing
        behavior) rather than assumed either way; DOB collection at registration is
        a follow-up needed to make safeguarding gates effective for new members.
        """
        if self.date_of_birth is None:
            return False
        today = timezone.localdate()
        age = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age < MINOR_AGE_THRESHOLD


class EmailVerificationToken(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        "identity.User",
        on_delete=models.CASCADE,
        related_name="email_verification_tokens",
    )
    token = models.CharField(max_length=128, unique=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "identity_email_verification_token"
        indexes = [
            models.Index(fields=["token"]),
        ]
