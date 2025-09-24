from django.db import models
from django.utils import timezone


# Define a base model class that includes common fields for all models
class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class BlankModel(models.Model):
    """
    A blank model that can be used as a placeholder or for testing purposes.
    """
