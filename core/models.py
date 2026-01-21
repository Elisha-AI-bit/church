from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import threading

_thread_locals = threading.local()

def get_current_church():
    return getattr(_thread_locals, 'church', None)

def set_current_church(church):
    _thread_locals.church = church

def clear_current_church():
    if hasattr(_thread_locals, 'church'):
        del _thread_locals.church

class Church(models.Model):
    """The tenant model representing a church congregation"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to='church_logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Churches"


class TenantManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        church = get_current_church()
        if church:
            return qs.filter(church=church)
        return qs


class TenantModel(models.Model):
    """Abstract base class for models that belong to a specific church"""
    church = models.ForeignKey(Church, on_delete=models.CASCADE, null=True, blank=True)
    
    objects = TenantManager()
    admin_objects = models.Manager()
    
    class Meta:
        abstract = True


class UserProfile(models.Model):
    """Link Django users to a specific church"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='user_profiles')
    
    def __str__(self):
        return f"{self.user.username} ({self.church.name})"


class Backup(models.Model):
    """Track database and media backups"""
    BACKUP_TYPE_CHOICES = [
        ('database', 'Database Only'),
        ('media', 'Media Files Only'),
        ('full', 'Full Backup (Database + Media)'),
    ]
    
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    filename = models.CharField(max_length=255)
    absolute_path = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file_size = models.BigIntegerField(default=0, help_text="Size in bytes")
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPE_CHOICES, default='full')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Backup'
        verbose_name_plural = 'Backups'
    
    def __str__(self):
        return f"{self.filename} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)


class BackupConfiguration(models.Model):
    """Configuration for automated backups"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    auto_backup_enabled = models.BooleanField(default=False)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    preferred_time = models.TimeField(default="00:00", help_text="What time should the backup run?")
    storage_path = models.CharField(max_length=500, blank=True, null=True, 
                                   help_text="Custom path for backups (e.g., E:\\Backups). Leave empty for default.")
    backup_type = models.CharField(max_length=20, choices=Backup.BACKUP_TYPE_CHOICES, default='full')
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Backup Configuration'
        verbose_name_plural = 'Backup Configurations'
    
    def __str__(self):
        status = "Enabled" if self.auto_backup_enabled else "Disabled"
        return f"Backup Config: {status} ({self.frequency} at {self.preferred_time})"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and BackupConfiguration.objects.exists():
            return
        
        # Initial next_run calculation if enabled and next_run is null
        if self.auto_backup_enabled and not self.next_run:
            from django.utils import timezone
            import datetime
            now = timezone.now()
            # Combine 'today' with 'preferred_time'
            scheduled_today = timezone.make_aware(
                datetime.datetime.combine(now.date(), self.preferred_time)
            )
            if scheduled_today <= now:
                # If the time has passed today, schedule for tomorrow
                self.next_run = scheduled_today + datetime.timedelta(days=1)
            else:
                self.next_run = scheduled_today
                
        super().save(*args, **kwargs)
