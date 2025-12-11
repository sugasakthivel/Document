import uuid
import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class SharedFile(models.Model):
    EXPIRY_CHOICES = [
        (1, '1 Hour'),
        (24, '24 Hours'),
        (72, '3 Days'),
        (168, '7 Days'),
        (720, '30 Days'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_files')
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    expiry_hours = models.IntegerField(choices=EXPIRY_CHOICES, default=24)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    max_downloads = models.IntegerField(default=0, help_text='0 = unlimited')
    download_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=self.expiry_hours)
        if not self.original_filename:
            self.original_filename = self.file.name
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at or not self.is_active
    
    def can_download(self):
        if self.is_expired():
            return False
        if self.max_downloads > 0 and self.download_count >= self.max_downloads:
            return False
        return True
    
    def __str__(self):
        return f"{self.original_filename} - {self.user.username}"
    
class DownloadLog(models.Model):
    shared_file = models.ForeignKey(SharedFile, on_delete=models.CASCADE, related_name='downloads')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-downloaded_at']
        indexes = [
            models.Index(fields=['shared_file', '-downloaded_at']),
        ]
    
    def __str__(self):
        return f"{self.shared_file.original_filename} - {self.ip_address}"