from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import TenantModel


class Project(TenantModel):
    """Church projects"""
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    FUNDING_TYPE = [
        ('internal', 'Internal Funding'),
        ('external', 'External Funding'),
        ('mixed', 'Mixed Funding'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    funding_type = models.CharField(max_length=20, choices=FUNDING_TYPE)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='proposed')
    start_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    actual_completion_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def remaining_budget(self):
        return self.total_budget - self.spent_amount
    
    @property
    def budget_utilization_percentage(self):
        if self.total_budget == 0:
            return 0
        return (self.spent_amount / self.total_budget) * 100
    
    class Meta:
        ordering = ['-created_at']


class ProjectFunding(TenantModel):
    """Funding sources for projects"""
    FUNDING_SOURCE_TYPE = [
        ('internal_church', 'Internal Church Funds'),
        ('donor', 'Donor/External Funding'),
        ('fundraising', 'Fundraising Event'),
        ('grant', 'Grant'),
        ('other', 'Other'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='funding_sources')
    source_type = models.CharField(max_length=30, choices=FUNDING_SOURCE_TYPE)
    source_name = models.CharField(max_length=200, help_text="Name of donor/organization/event")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    received_date = models.DateField()
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.project} - {self.source_name} ({self.amount})"
    
    class Meta:
        ordering = ['-received_date']


class ProjectAssignment(TenantModel):
    """Assign projects to groups or committees"""
    RESPONSIBLE_ENTITY_TYPE = [
        ('group', 'Group'),
        ('committee', 'Committee'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assignments')
    
    # Generic FK to either Group or Committee
    responsible_entity_type = models.CharField(max_length=20, choices=RESPONSIBLE_ENTITY_TYPE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    responsible_entity = GenericForeignKey('content_type', 'object_id')
    
    assigned_date = models.DateField()
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.project} - Assigned to {self.responsible_entity}"
    
    class Meta:
        ordering = ['-assigned_date']
