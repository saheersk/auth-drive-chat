from django.db import models
from django.conf import settings


class GoogleDriveToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expiry = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Google Drive Token for {self.user.email}"


class GoogleDriveFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    file_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=255)
    drive_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
