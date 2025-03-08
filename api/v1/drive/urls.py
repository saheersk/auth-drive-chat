from django.urls import path

from .views import google_drive_auth, google_drive_callback, \
    upload_to_google_drive, list_google_drive_files, download_google_drive_file


urlpatterns = [
    path("auth/", google_drive_auth, name="google-drive-auth"),
    path("callback/", google_drive_callback,
         name="google-drive-callback"),
    path("upload/", upload_to_google_drive, name="upload-file"),
    path("files/", list_google_drive_files, name="list-drive"),
    path("download/<int:file_id>/", download_google_drive_file,
         name="download-drive"),
]
