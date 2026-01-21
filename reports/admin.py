from django.contrib import admin
from .models import ReportTemplate, SavedReport


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'is_public', 'created_by', 'created_at']
    list_filter = ['report_type', 'is_public']
    search_fields = ['name', 'description']


@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'template', 'generated_by', 'generated_date']
    list_filter = ['generated_date']
    search_fields = ['title']
