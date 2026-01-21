from django.contrib import admin
from .models import Project, ProjectFunding, ProjectAssignment


class ProjectFundingInline(admin.TabularInline):
    model = ProjectFunding
    extra = 1


class ProjectAssignmentInline(admin.TabularInline):
    model = ProjectAssignment
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'funding_type', 'total_budget', 'spent_amount', 'start_date']
    list_filter = ['status', 'funding_type']
    search_fields = ['name', 'description']
    inlines = [ProjectFundingInline, ProjectAssignmentInline]


@admin.register(ProjectFunding)
class ProjectFundingAdmin(admin.ModelAdmin):
    list_display = ['project', 'source_type', 'source_name', 'amount', 'received_date']
    list_filter = ['source_type']
    search_fields = ['project__name', 'source_name']


@admin.register(ProjectAssignment)
class ProjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ['project', 'responsible_entity_type', 'assigned_date']
    list_filter = ['responsible_entity_type']
    search_fields = ['project__name']
