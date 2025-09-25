from django.contrib import admin
from common.models.Workspace import WorkspaceModel


@admin.register(WorkspaceModel)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_deleted', 'created_at')
    search_fields = ('name', 'user__username', 'user__email')
    readonly_fields = ('uid', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('uid', 'name', 'user', 'is_active')
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