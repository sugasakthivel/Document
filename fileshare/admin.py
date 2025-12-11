from django.contrib import admin
from .models import SharedFile, DownloadLog

@admin.register(SharedFile)
class SharedFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'user', 'created_at', 'expires_at', 'is_active', 'download_count']
    list_filter = ['is_active', 'created_at', 'expiry_hours']
    search_fields = ['original_filename', 'user__username', 'token']
    readonly_fields = ['token', 'created_at', 'download_count']
    date_hierarchy = 'created_at'

@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ['shared_file', 'ip_address', 'downloaded_at', 'success']
    list_filter = ['success', 'downloaded_at']
    search_fields = ['ip_address', 'shared_file__original_filename']
    readonly_fields = ['shared_file', 'ip_address', 'user_agent', 'downloaded_at', 'success']
    date_hierarchy = 'downloaded_at'
