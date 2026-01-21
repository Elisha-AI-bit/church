from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from core.models import TenantModel


class SpecialDay(TenantModel):
    """Special Events like New Year, Harvest, Christmas"""
    EVENT_TYPES = [
        ('harvest', 'Harvest (Dry/Green)'),
        ('holiday', 'Holiday (Xmas, New Year)'),
        ('special', 'Special Service'),
    ]
    
    name = models.CharField(max_length=200) # e.g. "Green Harvest 2024"
    date = models.DateField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Goals
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.date.year})"
    
    class Meta:
        ordering = ['-date']

class Pledge(TenantModel):
    """Promise to contribute"""
    event = models.ForeignKey(SpecialDay, on_delete=models.CASCADE, related_name='pledges')
    member = models.ForeignKey('membership.Member', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fulfilled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.member} pledged K{self.amount} to {self.event}"

class Donation(TenantModel):
    """Actual Contribution (Cash/Monetary)"""
    event = models.ForeignKey(SpecialDay, on_delete=models.CASCADE, related_name='donations')
    member = models.ForeignKey('membership.Member', on_delete=models.SET_NULL, null=True, blank=True)
    donor_name = models.CharField(max_length=100, blank=True, help_text="If not a member")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    date = models.DateField()
    
    # Link to main Finance Income (so it appears in main dashboard)
    finance_income = models.OneToOneField('finance.Income', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"K{self.amount} for {self.event}"

class HarvestItem(TenantModel):
    """In-Kind Donations (Maize, Chicken, etc.)"""
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('sold', 'Sold'),
        ('failed', 'Failed to Sell'),
        ('donated', 'Donated to the Needy'),
        ('kept', 'Kept for Church Use'),
        ('spoiled', 'Spoiled/Lost'),
    ]
    
    event = models.ForeignKey(SpecialDay, on_delete=models.CASCADE, related_name='items')
    member = models.ForeignKey('membership.Member', on_delete=models.SET_NULL, null=True, blank=True)
    donor_name = models.CharField(max_length=100, blank=True)
    
    item_name = models.CharField(max_length=200) # e.g. "50kg Maize"
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, help_text="Monetary equivalent value")
    reserve_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    
    # If sold
    sold_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    sold_date = models.DateField(null=True, blank=True)
    
    # Link to Finance when sold
    finance_income = models.OneToOneField('finance.Income', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.item_name} ({self.status})"
