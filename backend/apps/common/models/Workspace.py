import uuid
from django.db import models
from django.contrib.auth.models import User
from .Base import BaseModel


class WorkspaceModel(BaseModel):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="workspaces"
    )

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    class Meta:
        app_label = 'common'
        verbose_name = "Workspace"
        verbose_name_plural = "Workspaces"
        db_table = "workspaces"