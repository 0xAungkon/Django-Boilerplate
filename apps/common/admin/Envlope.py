from django.contrib import admin
from common.models import (
    EnvelopDocumentModel,
    EnvelopModel,
    EnvelopFieldModel,
    EnvelopValueModel,
)


@admin.register(EnvelopDocumentModel)
class EnvelopDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "uid",
        "file_name",
        "file_size",
        "uploaded_by",
        "status",
        "file_path",
        "created_at",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("file_name", "uploaded_by__username")
    list_filter = ("status", "is_deleted", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EnvelopModel)
class EnvelopAdmin(admin.ModelAdmin):
    list_display = (
        "uid",
        # "user",
        "document_id",
        "created_by",
        "status",
        "message_subject",
        "created_at",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("message_subject", "user__username")
    list_filter = ("status", "is_deleted", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EnvelopFieldModel)
class EnvelopFieldAdmin(admin.ModelAdmin):
    list_display = ("uid", "envelop_id", "created_at", "updated_at", "is_deleted")
    search_fields = ("envelop__uid",)
    list_filter = ("is_deleted",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(EnvelopValueModel)
class EnvelopValueAdmin(admin.ModelAdmin):
    list_display = ("uid", "envelop", "created_at", "updated_at", "is_deleted")
    search_fields = ("envelop__uid",)
    list_filter = ("is_deleted",)
    readonly_fields = ("created_at", "updated_at")
