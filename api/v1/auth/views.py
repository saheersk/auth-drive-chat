import json

from django.contrib.auth import get_user_model
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.authtoken.models import Token


User = get_user_model()


@csrf_exempt
def google_auth_callback(request):
    try:
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            return JsonResponse({"error": "No token provided"}, status=400)

        idinfo = id_token.verify_oauth2_token(token, requests.Request(),
                                              settings.GOOGLE_CLIENT_ID)

        google_id = idinfo["sub"]
        email = idinfo["email"]
        username = idinfo.get("name", "")
        profile_image = idinfo.get("picture", "")

        user, created = User.objects.get_or_create(
            google_id=google_id,
            defaults={"email": email, "username": username,
                      "profile_image": profile_image, "provider": "google"}
        )

        if not user.google_id:
            user.google_id = google_id
            user.save()

        token, _ = Token.objects.get_or_create(user=user)

        return JsonResponse({
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "profile_image": user.profile_image,
            "token": token.key
        })

    except ValueError:
        return JsonResponse({"error": "Invalid token"}, status=400)
