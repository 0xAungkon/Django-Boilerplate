from common.models import APITokenModel
from django.contrib import admin


@admin.register(APITokenModel)
class APITokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at")
    list_display_links = ("user",)
    # list_editable = ("token",)
    search_fields = ("token", "user__username")
