from django.db import models
from django.contrib.auth.models import User
from core.models import TenantModel


class Section(TenantModel):
    """Church sections for organizing members"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Position(TenantModel):
    """Church positions that members can hold"""
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=50, choices=[
        ('congregation', 'Congregation Level'),
        ('section', 'Section Level'),
        ('committee', 'Committee Level'),
        ('group', 'Group Level'),
    ])
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']


class Member(TenantModel):
    """Principal members of the church"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    MEMBERSHIP_STATUS = [
        ('communicant', 'Full Member (Communicant)'),
        ('catechumen', 'Catechumen'),
        ('adherent', 'Non-Communicant (Adherent)'),
    ]
    
    TRANSFER_TYPE = [
        ('new', 'New Member'),
        ('ucz_transfer', 'Transfer from UCZ Church'),
        ('other_transfer', 'Transfer from Other Church'),
    ]
    
    # Personal Information
    membership_number = models.CharField(max_length=20, unique=True, blank=True, help_text="Auto-generated unique ID")
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField()
    place_of_work = models.CharField(max_length=200, blank=True)
    
    # Church Information
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, related_name='members')
    membership_status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS)
    date_joined = models.DateField()
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPE, default='new')
    transfer_from = models.CharField(max_length=200, blank=True, help_text="Church name if transferred")
    
    # Family Information
    partner = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='spouse')
    
    # Current Positions
    current_positions = models.ManyToManyField(Position, blank=True, related_name='members')
    
    # Profile Photo
    photo = models.ImageField(upload_to='members/photos/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='members_created')
    
    def save(self, *args, **kwargs):
        if not self.membership_number:
            # Generate UCZ-00001
            last = Member.objects.filter(church=self.church).order_by('-id').first()
            if last and last.membership_number and last.membership_number.startswith('UCZ-'):
                try:
                    # Extract number part
                    last_num = int(last.membership_number.split('-')[1])
                    self.membership_number = f"UCZ-{last_num + 1:05d}"
                except (IndexError, ValueError):
                    # Fallback if format is somehow wrong
                    self.membership_number = f"UCZ-{last.id + 1:05d}"
            else:
                 # Initial start or if no previous members have codes
                 # If members exist but no codes, we might want to migrate them, 
                 # but for new ones, we assume numbering starts or continues based on count?
                 # Safer to query for any membership number to be sure
                last_code = Member.objects.filter(church=self.church).exclude(membership_number='').order_by('-membership_number').first()
                if last_code:
                     try:
                        last_num = int(last_code.membership_number.split('-')[1])
                        self.membership_number = f"UCZ-{last_num + 1:05d}"
                     except:
                        self.membership_number = "UCZ-00001"
                else:
                    self.membership_number = "UCZ-00001"
                    
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Member'
        verbose_name_plural = 'Members'


class Dependent(TenantModel):
    """Children and dependents of principal members"""
    MEMBERSHIP_STATUS = [
        ('communicant', 'Full Member (Communicant)'),
        ('catechumen', 'Catechumen'),
        ('adherent', 'Non-Communicant (Adherent)'),
        ('child', 'Child'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    principal_member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='dependents')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    membership_status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='child')
    date_joined = models.DateField(null=True, blank=True)
    
    # If they become a principal member
    became_principal_member = models.OneToOneField(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='was_dependent')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} (Dependent of {self.principal_member})"
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    class Meta:
        ordering = ['last_name', 'first_name']


class PositionHistory(TenantModel):
    """Historical record of positions held by members"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='position_history')
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.member} - {self.position} ({self.start_date})"
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Position History'
        verbose_name_plural = 'Position Histories'


class MemberTransfer(TenantModel):
    """Records of member transfers"""
    TRANSFER_TYPE = [
        ('incoming', 'Incoming Transfer'),
        ('outgoing', 'Outgoing Transfer'),
    ]
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='transfers')
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPE)
    from_church = models.CharField(max_length=200, blank=True)
    to_church = models.CharField(max_length=200, blank=True)
    transfer_date = models.DateField()
    approval_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.member} - {self.get_transfer_type_display()}"
    
    class Meta:
        ordering = ['-transfer_date']
