import uuid
from django.db import models
from django.contrib.auth.models import User
from .Base import BaseModel


class SSHCredsModel(BaseModel):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    public_key = models.TextField()
    private_key = models.TextField()
    name = models.TextField()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ssh_credentials"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    class Meta:
        app_label = 'common'
        verbose_name = "SSH Credential"
        verbose_name_plural = "SSH Credentials"
        db_table = "ssh_creds"