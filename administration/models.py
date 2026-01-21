from django.db import models
from django.contrib.auth.models import User
from core.models import Church, TenantModel, UserProfile
from membership.models import Member


class OfficeBearer(TenantModel):
    """Office bearers of the congregation"""
    POSITION_CHOICES = [
        ('chairperson', 'Congregation Chairperson (Reverend)'),
        ('secretary', 'Congregation Secretary'),
        ('vice_secretary', 'Congregation Vice Secretary'),
        ('treasurer', 'Congregation Treasurer'),
    ]
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='office_bearer_roles')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, unique=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.member} - {self.get_position_display()}"
    
    class Meta:
        ordering = ['position']


class ChurchCouncil(TenantModel):
    """Church council members"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='council_membership')
    role = models.CharField(max_length=100, help_text="e.g., Section Elder, Committee Convenor")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.member} - {self.role}"
    
    class Meta:
        ordering = ['member__last_name']


class LayLeader(TenantModel):
    """Lay leaders within the congregation"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='lay_leader_roles')
    specialty = models.CharField(max_length=200, help_text="Area of leadership/specialty")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.member} - Lay Leader ({self.specialty})"
    
    class Meta:
        ordering = ['member__last_name']


class ChurchElder(TenantModel):
    """Church elders and their sections"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='elder_roles')
    section = models.ForeignKey('membership.Section', on_delete=models.SET_NULL, null=True, related_name='elders')
    ordained_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Elder {self.member} - {self.section}"
    
    class Meta:
        ordering = ['section', 'member__last_name']


class Stewardship(TenantModel):
    """Stewardship members"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='stewardship_roles')
    role = models.CharField(max_length=100, choices=[
        ('convenor', 'Stewardship Convenor'),
        ('member', 'Stewardship Member'),
    ])
    section = models.ForeignKey('membership.Section', on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.member} - {self.get_role_display()}"
    
    class Meta:
        ordering = ['role', 'member__last_name']

class Department(TenantModel):
    """Organizational departments (e.g., HR, Finance, Sunday School)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    head = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        unique_together = ['church', 'name']
