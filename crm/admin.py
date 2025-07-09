from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Company, Storage

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_company_owner', 'company', 'is_staff', 'is_active')
    list_filter = ('is_company_owner', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'company__name')
    ordering = ('email',)

admin.site.register(Company)
admin.site.register(Storage)
