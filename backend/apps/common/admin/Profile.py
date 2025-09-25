from django.utils.html import format_html
from common.models.Profile import ProfileModel
from django.contrib import admin


@admin.register(ProfileModel)
class ProfileExtraInfoAdmin(admin.ModelAdmin):
    list_display = ("user", "signature_img_preview")

    def signature_img_preview(self, obj):
        if obj.signature_img:
            return format_html(
                '<img src="{}" width="100" height="50" />', obj.signature_img.url
            )
        return "-"

    signature_img_preview.short_description = "Signature Image"
