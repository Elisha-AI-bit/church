from django.db import models
from django.contrib.auth.models import User
from core.models import TenantModel


class EventCategory(TenantModel):
    """Categories for planner events (e.g., Sunday Service, Group Meeting)"""
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default='blue', help_text="Tailwind color name (e.g., blue, red, green)")
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Event Categories'

class Event(TenantModel):
    """Annual planner events"""
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, related_name='events')
    
    # Timing
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    # Location
    location = models.CharField(max_length=200, blank=True)
    
    # Budgeting
    budget_estimated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.start_date})"
    
    class Meta:
        ordering = ['start_date', 'start_time']

class SundayReport(TenantModel):
    """Report for Sunday Service Activities"""
    date = models.DateField()
    
    # Service Details
    preacher = models.CharField(max_length=200, blank=True)
    worship_leader = models.CharField(max_length=200, blank=True)
    section_on_duty = models.ForeignKey('membership.Section', on_delete=models.SET_NULL, null=True, blank=True, related_name='duty_sundays')
    
    # Attendance
    attendance_men = models.PositiveIntegerField(default=0)
    attendance_women = models.PositiveIntegerField(default=0)
    attendance_children = models.PositiveIntegerField(default=0)
    attendance_visitors = models.PositiveIntegerField(default=0)
    
    # Calculated Totals (denormalized for easy dashboard access)
    total_offering = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tithe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items_sale = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Total from sold items")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"Sunday Report - {self.date}"
    
    @property
    def grand_total(self):
        return self.total_offering + self.total_tithe + self.total_items_sale

    class Meta:
        ordering = ['-date']
        unique_together = ['church', 'date']

class SundayItem(TenantModel):
    """Items donated during Sunday Service"""
    STATUS_CHOICES = [
        ('sold', 'Sold'),
        ('failed', 'Failed to Sell'),
        ('donated', 'Donated to the Needy'),
        ('kept', 'Kept for Church Use'),
        ('pending', 'Pending / In Stock')
    ]
    
    report = models.ForeignKey(SundayReport, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2)
    reserve_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sold_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Actual amount realized if sold")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.item_name} ({self.status})"

class SectionFunds(TenantModel):
    """Collection breakdown by section"""
    report = models.ForeignKey(SundayReport, on_delete=models.CASCADE, related_name='section_funds')
    section = models.ForeignKey('membership.Section', on_delete=models.CASCADE)
    
    tithe_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    envelopes_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loose_offering_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    thanksgiving_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    @property
    def total(self):
        return self.tithe_amount + self.envelopes_amount + self.loose_offering_amount + self.thanksgiving_amount
        
    def __str__(self):
        return f"{self.section} Funds - {self.report.date}"
    
    class Meta:
        unique_together = [['report', 'section'], ['church', 'report', 'section']]
