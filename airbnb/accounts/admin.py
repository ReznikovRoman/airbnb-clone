from django.contrib import admin
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Profile, SMSLog
from .forms import AdminCustomUserChangeForm, SignUpForm


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'get_profile_link', 'is_email_confirmed')
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('id', 'date_joined', 'last_login')
    ordering = ('email',)

    list_filter = ('is_active', 'is_staff', 'is_admin')

    form = AdminCustomUserChangeForm
    fieldsets = (
        (None, {'fields': ('email',)}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_email_confirmed', 'is_staff', 'is_admin', 'groups', 'user_permissions')}
         ),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_form = SignUpForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')}
         ),
    )

    def get_profile_link(self, obj: CustomUser):
        return mark_safe(
            f"""<a href="{reverse('admin:accounts_profile_change', args=(obj.profile.id,))}">{obj.first_name}'s
            profile</a>"""
        )
    get_profile_link.short_description = 'profile link'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_of_birth', 'gender', 'phone_number')
    search_fields = ('user__email',)


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_profile_link')

    def get_profile_link(self, obj: CustomUser):
        return mark_safe(
            f"""<a href="{reverse('admin:accounts_profile_change', args=(obj.profile.id,))}">
            {obj.profile.user.first_name}'s profile</a>"""
        )
    get_profile_link.short_description = 'profile link'
