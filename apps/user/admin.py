from django.contrib import admin

from apps.common.admin import SoftDeleteAdminMixin
from .models import User, UserDevice


@admin.register(User)
class UserAdmin(SoftDeleteAdminMixin):
    model = User
    list_display = ('username', 'first_name', 'last_name', 'primary_phone', 'role', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'primary_phone', 'tg_username')


@admin.register(UserDevice)
class UserDeviceAdmin(SoftDeleteAdminMixin):
    list_display = ("user", "device_name", "ip_address", "last_login")
    readonly_fields = ("refresh_token",)
