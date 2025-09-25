from django.contrib import admin
from common.models.SSHCreds import SSHCredsModel


@admin.register(SSHCredsModel)
class SSHCredsAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_deleted', 'created_at')
    search_fields = ('name', 'user__username', 'user__email')
    readonly_fields = ('uid', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('uid', 'name', 'user', 'is_active')
        }),
        ('Keys', {
            'fields': ('public_key', 'private_key'),
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
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make private key field a textarea widget for better display
        if 'private_key' in form.base_fields:
            form.base_fields['private_key'].widget.attrs.update({'rows': 10, 'cols': 80})
        if 'public_key' in form.base_fields:
            form.base_fields['public_key'].widget.attrs.update({'rows': 3, 'cols': 80})
        return form