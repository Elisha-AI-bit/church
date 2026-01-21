from django.contrib import admin
from .models import SpecialDay, Pledge, Donation, HarvestItem

class HarvestItemInline(admin.TabularInline):
    model = HarvestItem
    extra = 1

class DonationInline(admin.TabularInline):
    model = Donation
    extra = 1

@admin.register(SpecialDay)
class SpecialDayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'event_type', 'target_amount')
    list_filter = ('event_type',)
    inlines = [HarvestItemInline, DonationInline]

@admin.register(HarvestItem)
class HarvestItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'event', 'estimated_value', 'status', 'sold_amount')
    list_filter = ('status', 'event')
    actions = ['mark_sold']

admin.site.register(Pledge)
admin.site.register(Donation)
