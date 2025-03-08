from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "username", "google_id", "provider",
                    "is_active", "is_staff", "created_at")
    list_filter = ("is_active", "is_staff", "provider")
    search_fields = ("email", "username", "google_id")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("username", "profile_image")}),
        ("OAuth Info", {"fields": ("google_id", "provider")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser",
                                    "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "username",
                       "provider", "is_active", "is_staff"),
        }),
    )


admin.site.register(User, CustomUserAdmin)
