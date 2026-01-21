from django.contrib import admin
from .models import Section, Position, Member, Dependent, PositionHistory, MemberTransfer


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'level']
    list_filter = ['level']
    search_fields = ['title']


class DependentInline(admin.TabularInline):
    model = Dependent
    fk_name = 'principal_member'
    extra = 1
    fields = ['first_name', 'last_name', 'gender', 'date_of_birth', 'membership_status']


class PositionHistoryInline(admin.TabularInline):
    model = PositionHistory
    extra = 0
    fields = ['position', 'start_date', 'end_date', 'notes']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['membership_number', 'get_full_name', 'gender', 'section', 'membership_status', 'get_positions', 'date_joined']
    list_display_links = ['membership_number', 'get_full_name']
    list_filter = ['membership_status', 'gender', 'section', 'transfer_type']
    search_fields = ['membership_number', 'first_name', 'last_name', 'email', 'phone']
    inlines = [DependentInline, PositionHistoryInline]
    filter_horizontal = ('current_positions',)
    fieldsets = (
        ('Personal Information', {
            'fields': ('membership_number', 'first_name', 'middle_name', 'last_name', 'gender', 'date_of_birth', 'photo')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address', 'place_of_work')
        }),
        ('Church Information', {
            'fields': ('section', 'membership_status', 'date_joined', 'transfer_type', 'transfer_from', 'current_positions')
        }),
        ('Family Information', {
            'fields': ('partner',)
        }),
    )
    
    @admin.display(description='Full Name', ordering='last_name')
    def get_full_name(self, obj):
        return obj.full_name

    @admin.display(description='Positions')
    def get_positions(self, obj):
        return ", ".join([p.title for p in obj.current_positions.all()])


@admin.register(Dependent)
class DependentAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'principal_member', 'gender', 'get_age', 'membership_status']
    list_filter = ['membership_status', 'gender']
    search_fields = ['first_name', 'last_name', 'principal_member__first_name', 'principal_member__last_name']
    
    @admin.display(description='Full Name', ordering='last_name')
    def get_full_name(self, obj):
        return obj.full_name
    
    @admin.display(description='Age')
    def get_age(self, obj):
        return obj.age


@admin.register(PositionHistory)
class PositionHistoryAdmin(admin.ModelAdmin):
    list_display = ['member', 'position', 'start_date', 'end_date']
    list_filter = ['position', 'start_date']
    search_fields = ['member__first_name', 'member__last_name']


@admin.register(MemberTransfer)
class MemberTransferAdmin(admin.ModelAdmin):
    list_display = ['member', 'transfer_type', 'transfer_date', 'approval_status']
    list_filter = ['transfer_type', 'approval_status']
    search_fields = ['member__first_name', 'member__last_name', 'from_church', 'to_church']
