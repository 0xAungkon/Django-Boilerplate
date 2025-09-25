import uuid
from django.db import models
from django.contrib.auth.models import User
from .Base import BaseModel
from .Vault import VaultModel
from .SSHCreds import SSHCredsModel


class SSHServersModel(BaseModel):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    server_host = models.TextField()
    server_port = models.IntegerField(default=22)
    server_user = models.TextField()
    private_key = models.TextField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    creds = models.ForeignKey(
        SSHCredsModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ssh_servers"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ssh_servers"
    )
    vault = models.ForeignKey(
        VaultModel,
        on_delete=models.CASCADE,
        related_name="ssh_servers"
    )
    alias = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.alias or self.server_host}:{self.server_port} - {self.user.username}"

    class Meta:
        app_label = 'common'
        verbose_name = "SSH Server"
        verbose_name_plural = "SSH Servers"
        db_table = "ssh_servers"