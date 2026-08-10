from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from apps.accounts.models import ApplicantProfile


class ApplicantProfileInline(admin.StackedInline):
    model = ApplicantProfile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = [ApplicantProfileInline]
    list_display = BaseUserAdmin.list_display + ("get_groups",)

    @admin.display(description="Grupos")
    def get_groups(self, user):
        return ", ".join(group.name for group in user.groups.all())


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
