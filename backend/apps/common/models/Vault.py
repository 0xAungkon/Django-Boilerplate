import uuid
from django.db import models
from django.contrib.auth.models import User
from .Base import BaseModel


class VaultModel(BaseModel):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_uid = models.UUIDField()
    meta_data = models.JSONField(null=True, blank=True)
    os_hostname = models.TextField()
    os_user = models.TextField()
    os_base = models.TextField()
    vault_name = models.TextField()
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vaults"
    )

    def __str__(self):
        return f"{self.vault_name} - {self.os_hostname}"

    class Meta:
        app_label = 'common'
        verbose_name = "Vault"
        verbose_name_plural = "Vaults"
        db_table = "vaults"