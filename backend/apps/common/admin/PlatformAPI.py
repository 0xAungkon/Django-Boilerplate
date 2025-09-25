from common.models import APITokenModel
from django.contrib import admin


@admin.register(APITokenModel)
class APITokenAdmin(admin.ModelAdmin):
    list_display = ('uid', 'title', 'user', 'token_preview', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_deleted', 'created_at')
    search_fields = ('title', 'user__username', 'user__email', 'token')
    readonly_fields = ('uid', 'token', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('uid', 'title', 'user', 'token', 'is_active')
        }),
        ('Policy', {
            'fields': ('policy',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Deletion', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        })
    )
    
    def token_preview(self, obj):
        """Show first 8 characters of token for security"""
        return f"{obj.token[:8]}..." if obj.token else ""
    token_preview.short_description = "Token Preview"
