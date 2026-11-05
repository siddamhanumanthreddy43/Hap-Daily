from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('FreshDairy Profile', {
            'fields': ('role', 'phone', 'delivery_address', 'city', 'pincode')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('FreshDairy Profile', {
            'fields': ('role', 'phone', 'delivery_address', 'city', 'pincode')
        }),
    )
