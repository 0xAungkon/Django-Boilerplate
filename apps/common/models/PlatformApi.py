import secrets
import base64
from django.db import models
from django.contrib.auth.models import User
from .Base import BaseModel
import uuid


def generate_token():
    return base64.urlsafe_b64encode(secrets.token_bytes(64)).decode()


class APITokenManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class APITokenModel(BaseModel):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_tokens")
    token = models.CharField(
        max_length=255, unique=True, default=generate_token, db_index=True
    )

    def is_valid(self):
        if self.is_deleted:
            return False

        return True
