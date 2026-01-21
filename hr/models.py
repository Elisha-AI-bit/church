from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from core.models import TenantModel


class PayGrade(TenantModel):
    """Employee Pay Grade and Leave Configuration"""
    name = models.CharField(max_length=50)
    monthly_leave_days = models.DecimalField(max_digits=4, decimal_places=2, help_text="Days accrued per month")
    
    def __str__(self):
        return f"{self.name} ({self.monthly_leave_days} days/month)"
    
    class Meta:
        unique_together = ['church', 'name']

class Employee(TenantModel):
    """Church Worker/Employee details"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], default='Male')
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    role = models.CharField(max_length=100)
    pay_grade = models.ForeignKey(PayGrade, on_delete=models.SET_NULL, null=True, blank=True)
    
    date_joined = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Financial Details
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    housing_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    education_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Leave Tracking
    leave_days_accrued = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    nrc_number = models.CharField(max_length=20, blank=True, verbose_name="NRC Number")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        unique_together = ['church', 'email']
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class PayrollPeriod(TenantModel):
    """Payroll month (e.g., October 2025)"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('locked', 'Locked (Processing)'),
        ('paid', 'Paid'),
    ]
    
    month = models.DateField(help_text="Select any day in the month (e.g., 1st)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_payrolls')
    paid_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-month']
        unique_together = ['church', 'month']
        
    def __str__(self):
        return self.month.strftime("%B %Y")
        
    @property
    def total_payout(self):
        return sum(slip.net_pay for slip in self.payslips.all())

class Payslip(TenantModel):
    """Individual payslip for an employee"""
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='payslips')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payslips')
    
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Allowances Breakdown
    housing_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    education_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Statutory Deductions
    pension_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="NAPSA (5%)")
    nhima_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="NHIMA (1%)")
    paye_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="PAYE Tax")
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Totals
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay_calculated = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Snapshot of details at time of generation
    role_at_time = models.CharField(max_length=100, blank=True)
    
    # Leave Details for this period
    leave_days_balance = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    leave_pay_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    bank_details_snapshot = models.TextField(blank=True) # JSON or text summary
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['payroll_period', 'employee'], ['church', 'payroll_period', 'employee']]
        
    @property
    def net_pay(self):
        return self.net_pay_calculated
    
    @property
    def total_deductions(self):
        """Calculate total statutory deductions"""
        return self.pension_deduction + self.nhima_deduction + self.paye_tax + self.other_deductions
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.payroll_period}"
