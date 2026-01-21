from django.db import models
from membership.models import Member
from core.models import TenantModel


class Committee(TenantModel):
    """Church committees"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    meeting_schedule = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        unique_together = ['church', 'name']


class CommitteeLeadership(TenantModel):
    """Leadership for each committee"""
    LEADERSHIP_ROLES = [
        ('convenor', 'Convenor'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
    ]
    
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name='leadership')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='committee_leadership_roles')
    role = models.CharField(max_length=20, choices=LEADERSHIP_ROLES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.member} - {self.get_role_display()} of {self.committee}"
    
    class Meta:
        ordering = ['committee', 'role']
        unique_together = ['church', 'committee', 'role', 'is_active']


class CommitteeMembership(TenantModel):
    """Members belonging to committees"""
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='committee_memberships')
    joined_date = models.DateField()
    left_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.member} - {self.committee}"
    
    class Meta:
        ordering = ['committee', 'member__last_name']
        unique_together = ['church', 'committee', 'member']
