from django.contrib import admin
from common.models.Vault import VaultModel


@admin.register(VaultModel)
class VaultAdmin(admin.ModelAdmin):
    list_display = ('uid', 'vault_name', 'os_hostname', 'os_user', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_deleted', 'os_base', 'created_at')
    search_fields = ('vault_name', 'os_hostname', 'os_user', 'user__username')
    readonly_fields = ('uid', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('uid', 'vault_name', 'device_uid', 'user')
        }),
        ('OS Information', {
            'fields': ('os_hostname', 'os_user', 'os_base')
        }),
        ('Metadata', {
            'fields': ('meta_data',),
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