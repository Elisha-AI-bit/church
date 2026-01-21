from django.db import models
from django.contrib.auth.models import User
from core.models import TenantModel


class ReportTemplate(TenantModel):
    """Customizable report templates"""
    REPORT_TYPES = [
        ('membership', 'Membership Report'),
        ('finance', 'Financial Report'),
        ('groups', 'Groups Report'),
        ('committees', 'Committees Report'),
        ('projects', 'Projects Report'),
        ('attendance', 'Attendance Report'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=dict, help_text="Report parameters and filters")
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_templates')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class SavedReport(TenantModel):
    """User-saved reports"""
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    report_data = models.JSONField(help_text="Cached report data")
    generated_date = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.title} - {self.generated_date}"
    
    class Meta:
        ordering = ['-generated_date']
