from django.contrib import admin
from common.models.SSHServers import SSHServersModel


@admin.register(SSHServersModel)
class SSHServersAdmin(admin.ModelAdmin):
    list_display = ('uid', 'alias', 'server_host', 'server_port', 'server_user', 'vault', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_deleted', 'server_port', 'created_at')
    search_fields = ('alias', 'server_host', 'server_user', 'user__username', 'vault__vault_name')
    readonly_fields = ('uid', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('uid', 'alias', 'user', 'vault')
        }),
        ('Server Details', {
            'fields': ('server_host', 'server_port', 'server_user')
        }),
        ('Authentication', {
            'fields': ('creds', 'private_key'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
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
        return form