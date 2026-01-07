from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import User, PasswordResetOTP, RegistrationOTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields shown in admin list
    list_display = (
        "user_id",
        "profile_thumb",
        "username",
        "email",
        "phone_number",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "created_at",
    )
    list_filter = ("is_active", "is_staff", "country", "state", "created_at")
    search_fields = ("username", "email", "phone_number", "first_name", "last_name")
    ordering = ("username",)
    readonly_fields = (
        "user_id",
        "date_joined",
        "created_at",
        "updated_at",
        "last_login",
        "profile_preview",
    )

    # Small thumbnail in list
    def profile_thumb(self, obj):
        if obj.profile_photo:
            return format_html(
                '<a href="{url}" target="_blank">'
                '<img src="{url}" width="40" height="40" '
                'style="border-radius:50%; object-fit:cover; box-shadow:0 0 2px #777;" />'
                '</a>',
                url=obj.profile_photo.url,
            )
        return "—"

    profile_thumb.short_description = "Profile"

    # Larger preview in detail page
    def profile_preview(self, obj):
        if obj.profile_photo:
            return format_html(
                '<a href="{url}" target="_blank">'
                '<img src="{url}" width="100" height="100" '
                'style="border-radius:10px; object-fit:cover; box-shadow:0 0 4px #555;" />'
                '</a>',
                url=obj.profile_photo.url,
            )
        return "—"

    profile_preview.short_description = "Profile Preview"

    # Fieldsets for editing an existing user
    fieldsets = (
        (None, {"fields": ("user_id", "username", "email", "phone_number", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "date_of_birth",
                    "address",
                    "pincode",
                    "state",
                    "country",
                    "profile_photo",
                    "profile_preview",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {"fields": ("last_login", "date_joined", "created_at", "updated_at")},
        ),
    )

    # Fieldsets for adding a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "phone_number",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    # Custom admin header showing total users
    def changelist_view(self, request, extra_context=None):
        total_users = User.objects.count()
        extra_context = extra_context or {}
        extra_context["title"] = _(f"Users (Total: {total_users})")
        return super().changelist_view(request, extra_context=extra_context)



@admin.register(RegistrationOTP)
class RegistrationOTPAdmin(admin.ModelAdmin):
    list_display = ("email", "phone_number", "otp", "created_at", "expires_at", "is_expired_display")
    list_filter = ("created_at", "expires_at")
    search_fields = ("email", "phone_number", "otp")
    readonly_fields = ("created_at",)

    def is_expired_display(self, obj):
        return obj.is_expired()
    is_expired_display.short_description = "Expired?"
    is_expired_display.boolean = True


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "created_at", "expires_at", "is_expired_display")
    list_filter = ("created_at", "expires_at")
    search_fields = ("user__email", "user__username", "otp")
    readonly_fields = ("created_at",)

    def is_expired_display(self, obj):
        return obj.is_expired()
    is_expired_display.short_description = "Expired?"
    is_expired_display.boolean = True
