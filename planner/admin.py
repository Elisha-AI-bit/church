from django.contrib import admin
from .models import Event, EventCategory, SundayReport, SectionFunds

admin.site.register(Event)
admin.site.register(EventCategory)

class SectionFundsInline(admin.TabularInline):
    model = SectionFunds
    extra = 1

@admin.register(SundayReport)
class SundayReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'preacher', 'attendance_men', 'attendance_women', 'attendance_children')
    inlines = [SectionFundsInline]
