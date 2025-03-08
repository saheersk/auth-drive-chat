import requests
import datetime
import json

from django.utils.timezone import now
from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


from drive.models import GoogleDriveToken


GOOGLE_DRIVE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_DRIVE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_DRIVE_REDIRECT_URI = settings.DRIVE_REDIRECT_URI


def google_drive_auth(request):
    redirect_uri = GOOGLE_DRIVE_REDIRECT_URI
    client_id = settings.DRIVE_CLIENT_ID
    scope = "https://www.googleapis.com/auth/drive.file"

    auth_url = (
        f"{GOOGLE_DRIVE_AUTH_URL}?response_type=code&client_id={client_id}"
        f"&redirect_uri={redirect_uri}&scope={scope}&access_type=offline&prompt=consent"
    )
    return redirect(auth_url)


def google_drive_callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Authorization code not provided"},
                            status=400)

    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.DRIVE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_DRIVE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(GOOGLE_DRIVE_TOKEN_URL, data=data)
    token_data = response.json()

    if "access_token" not in token_data:
        return JsonResponse({"error": "Failed to obtain access token"},
                            status=400)

    user = request.user
    GoogleDriveToken.objects.update_or_create(
        user=user,
        defaults={
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token", ""),
            "expires_at": now() + datetime.timedelta(
                seconds=token_data["expires_in"]),
        },
    )

    return JsonResponse({"message": "Google Drive connected successfully"})


GOOGLE_DRIVE_UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"


def upload_to_google_drive(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests allowed"},
                            status=405)

    if not request.FILES.get("file"):
        return JsonResponse({"error": "No file provided"}, status=400)

    user = request.user
    token_obj = GoogleDriveToken.objects.filter(user=user).first()
    if not token_obj or token_obj.is_expired():
        return JsonResponse({"error": "Google Drive authentication required"},
                            status=401)

    file = request.FILES["file"]
    temp_file_path = default_storage.save(file.name, ContentFile(file.read()))

    headers = {
        "Authorization": f"Bearer {token_obj.access_token}"
    }

    metadata = {
        "name": file.name
    }

    files = {
        "metadata": ("metadata.json", json.dumps(metadata),
                     "application/json"),
        "file": (file.name, open(temp_file_path, "rb"), file.content_type),
    }

    try:
        response = requests.post(GOOGLE_DRIVE_UPLOAD_URL, headers=headers,
                                 files=files)
        response_data = response.json()

        if response.status_code != 200:
            return JsonResponse({"error": "Failed to upload file",
                                 "details": response_data}, status=400)

        return JsonResponse({"message": "File uploaded successfully",
                             "file_id": response_data["id"]})
    finally:
        default_storage.delete(temp_file_path)


GOOGLE_DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"


def list_google_drive_files(request):
    user = request.user
    token_obj = GoogleDriveToken.objects.filter(user=user).first()
    if not token_obj or token_obj.is_expired():
        return JsonResponse({"error": "Google Drive authentication required"}, status=401)

    headers = {
        "Authorization": f"Bearer {token_obj.access_token}"
    }

    response = requests.get(GOOGLE_DRIVE_FILES_URL, headers=headers)
    files_data = response.json()

    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch files", "details": files_data}, status=400)

    return JsonResponse(files_data)


GOOGLE_DRIVE_DOWNLOAD_URL = "https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"


def download_google_drive_file(request, file_id):
    user = request.user
    token_obj = GoogleDriveToken.objects.filter(user=user).first()
    if not token_obj or token_obj.is_expired():
        return JsonResponse({"error": "Google Drive authentication required"},
                            status=401)

    headers = {
        "Authorization": f"Bearer {token_obj.access_token}"
    }

    response = requests.get(GOOGLE_DRIVE_DOWNLOAD_URL.format(file_id=file_id),
                            headers=headers, stream=True)

    if response.status_code != 200:
        return JsonResponse({"error": "Failed to download file"}, status=400)

    response_content = response.content
    response_headers = {
        "Content-Type": response.headers["Content-Type"],
        "Content-Disposition": f"attachment; filename={file_id}"
    }

    return JsonResponse(response_content, safe=False, headers=response_headers)
