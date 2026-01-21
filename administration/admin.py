from django.contrib import admin
from core.models import Church, UserProfile
from .models import OfficeBearer, ChurchCouncil, LayLeader, ChurchElder, Stewardship, Department
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Re-register UserAdmin to ensure it's editable
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Church Profile'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin with Church profile"""
    inlines = (UserProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)




@admin.register(OfficeBearer)
class OfficeBearerAdmin(admin.ModelAdmin):
    list_display = ['member', 'position', 'start_date', 'end_date', 'is_active']
    list_filter = ['position', 'is_active']
    search_fields = ['member__first_name', 'member__last_name']


@admin.register(ChurchCouncil)
class ChurchCouncilAdmin(admin.ModelAdmin):
    list_display = ['member', 'role', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['member__first_name', 'member__last_name', 'role']


@admin.register(LayLeader)
class LayLeaderAdmin(admin.ModelAdmin):
    list_display = ['member', 'specialty', 'start_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['member__first_name', 'member__last_name', 'specialty']


@admin.register(ChurchElder)
class ChurchElderAdmin(admin.ModelAdmin):
    list_display = ['member', 'section', 'ordained_date', 'is_active']
    list_filter = ['section', 'is_active']
    search_fields = ['member__first_name', 'member__last_name']


@admin.register(Stewardship)
class StewardshipAdmin(admin.ModelAdmin):
    list_display = ['member', 'role', 'section', 'start_date', 'is_active']
    list_filter = ['role', 'section', 'is_active']
    search_fields = ['member__first_name', 'member__last_name']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head', 'created_at']
    search_fields = ['name', 'description']
