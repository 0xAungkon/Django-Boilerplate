import uuid
from django.db import models
from django.conf import settings
import common
from .Base import BaseModel
from core.helpers.ModelField import DocumentField
from storages.backends.s3boto3 import S3Boto3Storage
from django.contrib.postgres.indexes import GinIndex
from loguru import logger


def get_document_path(instance, filename):
    # Store files in MEDIA_ROOT/envelop_documents/<uuid>/<filename>
    return f"envelop_documents/{instance.uid}"


class EnvelopDocumentModel(BaseModel):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # TODO: file size and uploaded_by/created_by fields should be fix before deploy
    file_name = models.CharField(max_length=255)
    # deprecated: file_size can be calculated from the file field
    file_size = models.IntegerField()
    # deprecated
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    file_path = DocumentField(
        upload_to=get_document_path,
        null=True,
        blank=True,
        storage=S3Boto3Storage,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_documents",
    )

    class Meta:
        verbose_name = "Envelop Document"
        verbose_name_plural = "Envelop Documents"


class EnvelopModel(BaseModel):
    ENVELOPE_TYPE_CHOICESS = [
        ("Certified", "Certified"),
        ("Standard", "Standard"),
        ("Legal", "Legal"),
        ("Custom", "Custom"),
        ("Other", "Other"),
    ]


    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document_id = models.ForeignKey(
        EnvelopDocumentModel,
        on_delete=models.CASCADE,
        related_name="envelops",
        null=False,
        blank=False,
    )
    status = models.CharField(
        max_length=255,
        help_text="initalized, stage1, stage2, stage3, stage4, done, cancelled, expired",
        default="0",
    )
    message_subject = models.CharField(max_length=255)
    message_body = models.TextField()
    recipients: dict[
        str,
        "common.controllers.Envelop.EnvelopRecipentsController.EnvelopRecipientSerializer",
    ] = models.JSONField()

    envelope_type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default="Standard",
        choices=ENVELOPE_TYPE_CHOICESS,
    )
    ref_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reference ID for the envelope, can be used for tracking or linking to external systems.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_envelops",
    )

    class Meta:
        verbose_name = "Envelop"
        verbose_name_plural = "Envelops"
        indexes = [
            GinIndex(fields=["recipients"]),
        ]

    @classmethod
    def get_envelop_by_user(cls, user, objs=None):
        if objs is None:
            objs = cls.objects
        return objs.filter(created_by=user).order_by("-created_at")

    @classmethod
    def get_envelop_by_recipients_key(cls, key, objs=None):
        if objs is None:
            objs = cls.objects
        return objs.filter(recipients__has_key=key)

    @classmethod
    def get_envelop_by_recipients_mail(cls, mail, objs=None):
        if objs is None:
            objs = cls.objects
        return cls.get_envelop_by_recipients_key(mail, objs)

    @classmethod
    def get_envelops_by_recipients_mail_or_user(cls, user, objs=None):
        """
        Get envelopes where the user is either the recipient or the creator.
        This method combines both recipient and user filters.
        """
        return (
            cls.get_envelop_by_user(user,objs)
            | cls.get_envelop_by_recipients_mail(user.email, objs)
        ).distinct()

    def update_current_stage(self, value: str):
        """Set the current stage of the envelope based on its status."""
        if value:
            self.status = value
        if int(self.status) - 1 < len(self.recipients):
            self.status = str(int(self.status) + 1)
        else:
            self.status = "done"
        self.save()

    def get_current_stage_for_user_mail(self, user_mail: str) -> tuple[int, str]:
        """
        Get the current stage of the envelope based on its status.
        """
        # stages = {
        #     pass
        # }

        try:
            mail_status = self.status
            try:
                mail_status = int(self.status)
            except ValueError:
                if mail_status == "done":
                    return (5, "Completed")
                if mail_status == "cancelled":
                    return (6, "Cancelled")
                if mail_status == "expired":
                    return (7, "Expired")
            if self.created_by.email == user_mail:
                return (8, "Sent Successfully.")
            user_order = self.recipients[user_mail].get("order")
        except KeyError as e:
            logger.trace(e)
            logger.error(f"Unknown recipient: {user_mail} in envelope {self.uid}")
            return (9, "ERROR: Unknown recipient. Not available in recipients list.")
        if mail_status == 0:
            return (0, "Initialized")
        if mail_status < user_order:
            return (1, "Waiting for others to compelete")
        if mail_status == user_order:
            return (2, "Waiting for you to sign")
        if mail_status < len(self.recipients) and mail_status > user_order:
            return (3, "Waiting for others to sign")
        if mail_status == len(self.recipients):
            return (4, "Waiting for finalization")

        return (9, "Unknown")


class EnvelopFieldModel(BaseModel):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    envelop = models.OneToOneField(
        EnvelopModel, on_delete=models.CASCADE, related_name="field"
    )
    field_data = models.JSONField()

    class Meta:
        verbose_name = "Envelop Field"
        verbose_name_plural = "Envelop Fields"


class EnvelopTemplateModel(BaseModel):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document_id = models.ForeignKey(
        EnvelopDocumentModel,
        on_delete=models.CASCADE,
        related_name="envelop_templates",
        null=False,
        blank=False,
    )
    message_subject = models.CharField(max_length=255)
    message_body = models.TextField()
    recipients = models.JSONField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_envelop_templates",
    )

    class Meta:
        verbose_name = "Envelop"
        verbose_name_plural = "Envelops"


class EnvelopFieldTemplateModel(BaseModel):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    envelop = models.OneToOneField(EnvelopTemplateModel, on_delete=models.CASCADE)
    field_data = models.JSONField()

    class Meta:
        verbose_name = "Envelop Field"
        verbose_name_plural = "Envelop Fields"


class EnvelopValueModel(BaseModel):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    envelop = models.ForeignKey(
        EnvelopModel, on_delete=models.CASCADE, related_name="values"
    )
    # TODO : PREVENT DUPLICATION IN FIELD DATA
    field_data = models.JSONField()

    class Meta:
        verbose_name = "Envelop Value"
        verbose_name_plural = "Envelop Values"
