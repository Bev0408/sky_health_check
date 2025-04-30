from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'department', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'role', 'department')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'email')}),
        (_('Role and Department'), {'fields': ('role', 'department')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('username', 'full_name', 'email')
    ordering = ('username',)


admin.site.register(User, UserAdmin)
