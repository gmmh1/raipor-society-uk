import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "identity_role"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.code}: {self.name}"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    roles = models.ManyToManyField(Role, blank=True, related_name="users")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "identity_user"
        indexes = [
            models.Index(fields=["created_at"]),
        ]
