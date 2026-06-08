from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, EmailVerificationToken


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'student_name', 'college_name', 'is_college_representative', 'is_email_verified', 'is_staff']
    list_filter = ['is_college_representative', 'is_email_verified', 'is_staff']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('student_name', 'college_name', 'branch', 'year', 'city', 'address', 'phone_number', 'id_card_photo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_email_verified', 'is_college_representative')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'student_name', 'college_name', 'branch', 'year', 'city', 'address', 'phone_number', 'password1', 'password2'),
        }),
    )
    search_fields = ['email', 'student_name', 'college_name']
    ordering = ['email']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(EmailVerificationToken)