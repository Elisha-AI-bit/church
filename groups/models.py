from django.db import models
from membership.models import Member
from core.models import TenantModel


class Group(TenantModel):
    """Church groups"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    meeting_schedule = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        unique_together = ['church', 'name']


class GroupLeadership(TenantModel):
    """Leadership for each group"""
    LEADERSHIP_ROLES = [
        ('convenor', 'Convenor'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='leadership')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='group_leadership_roles')
    role = models.CharField(max_length=20, choices=LEADERSHIP_ROLES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.member} - {self.get_role_display()} of {self.group}"
    
    class Meta:
        ordering = ['group', 'role']
        unique_together = ['church', 'group', 'role', 'is_active']


class GroupMembership(TenantModel):
    """Members belonging to groups"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='group_memberships')
    joined_date = models.DateField()
    left_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.member} - {self.group}"
    
    class Meta:
        ordering = ['group', 'member__last_name']
        unique_together = ['church', 'group', 'member']
