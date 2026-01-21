from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import TenantModel


class BankAccount(TenantModel):
    """Church bank accounts"""
    account_name = models.CharField(max_length=200)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_type = models.CharField(max_length=50, choices=[
        ('savings', 'Savings Account'),
        ('checking', 'Checking Account'),
        ('project', 'Project Account'),
    ])
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.account_name} - {self.bank_name}"
    
    class Meta:
        ordering = ['account_name']


class IncomeCategory(TenantModel):
    """Income categories/streams"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Income Categories'
        unique_together = ['church', 'name']


class ExpenseCategory(TenantModel):
    """Expense categories/streams with hierarchy and type support"""
    CATEGORY_TYPES = [
        ('pe', 'Personal Emoluments (Staff)'),
        ('admin', 'Administrative Expenses'),
        ('dept', 'Departmental Budgets'),
        ('group', 'Groups and Sections'),
        ('court', 'Higher Court Obligations'),
        ('other', 'Other Operating Expenses'),
    ]
    
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    description = models.TextField(blank=True)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default='admin')
    expense_type = models.CharField(max_length=10, choices=[('opex', 'Operational Expenditure (OPEX)'), ('capex', 'Capital Expenditure (CAPEX)')], default='opex')
    is_remittance = models.BooleanField(default=False, help_text="Is this a remittance to higher courts?")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name
    
    class Meta:
        ordering = ['category_type', 'name']
        verbose_name_plural = 'Expense Categories'
        unique_together = ['church', 'name', 'parent']


class RemittanceSettings(TenantModel):
    """Settings for remittance percentages to higher courts"""
    REMITTANCE_TYPE = [
        ('synod', 'Synod'),
        ('synod_hc', 'Synod Holy Communion'),
        ('presbytery', 'Presbytery'),
        ('consistory', 'Consistory'),
    ]
    
    remittance_type = models.CharField(max_length=20, choices=REMITTANCE_TYPE)
    percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of applicable income to remit"
    )
    applicable_to_categories = models.ManyToManyField(
        IncomeCategory,
        help_text="Income categories this remittance applies to"
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_remittance_type_display()} - {self.percentage}%"
    
    class Meta:
        verbose_name = 'Remittance Setting'
        verbose_name_plural = 'Remittance Settings'
        unique_together = ['church', 'remittance_type']


class Income(TenantModel):
    """Income transactions"""
    category = models.ForeignKey(IncomeCategory, on_delete=models.PROTECT, related_name='incomes')
    bank_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name='incomes')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    transaction_date = models.DateField()
    receipt_number = models.CharField(max_length=50, blank=True)
    payer_name = models.CharField(max_length=200, blank=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('other', 'Other'),
    ])
    description = models.TextField(blank=True)
    
    # Auto-calculated remittances
    remittances_calculated = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.category} - {self.amount} on {self.transaction_date}"
    
    class Meta:
        ordering = ['-transaction_date']


class Expense(TenantModel):
    """Expense transactions"""
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    bank_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name='expenses')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    transaction_date = models.DateField()
    voucher_number = models.CharField(max_length=50, blank=True)
    payee_name = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('other', 'Other'),
    ])
    description = models.TextField()
    receipt_file = models.FileField(upload_to='receipts/', blank=True, null=True)
    
    # Link to remittance if this is auto-generated
    related_income = models.ForeignKey(Income, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_expenses')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.category} - {self.amount} on {self.transaction_date}"
    
    class Meta:
        ordering = ['-transaction_date']


class Remittance(TenantModel):
    """Track remittances to higher courts"""
    income = models.ForeignKey(Income, on_delete=models.CASCADE, related_name='remittances')
    remittance_setting = models.ForeignKey(RemittanceSettings, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    percentage_used = models.DecimalField(max_digits=5, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    expense = models.OneToOneField(Expense, on_delete=models.SET_NULL, null=True, blank=True, related_name='remittance_record')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.remittance_setting} - {self.amount} from {self.income}"
    
    class Meta:
        ordering = ['-created_at']


class Assessment(TenantModel):
    """Fixed assessments from higher courts"""
    ASSESSMENT_TYPE = [
        ('synod', 'Synod Assessment'),
        ('presbytery', 'Presbytery Assessment'),
        ('consistory', 'Consistory Assessment'),
    ]
    
    FREQUENCY = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ]
    
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    frequency = models.CharField(max_length=20, choices=FREQUENCY)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    expense = models.OneToOneField(Expense, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessment_record')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_assessment_type_display()} - {self.amount} (Due: {self.due_date})"
    
    class Meta:
        ordering = ['-due_date']


class AnnualBudget(TenantModel):
    """Annual Budget for the church with approval control"""
    BUDGET_STATUS = [
        ('draft', 'Draft (Open for Edits)'),
        ('review', 'Under Review'),
        ('locked', 'Locked (Approved)'),
        ('closed', 'Closed (Financial Year Ended)'),
    ]
    
    year = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    status = models.CharField(max_length=20, choices=BUDGET_STATUS, default='draft')
    is_locked = models.BooleanField(default=False, help_text="Lock budget lines from further editing")
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Explanations/Notes for this financial year")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_budgets')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Budget {self.year} ({self.get_status_display()})"
    
    def lock(self, user):
        self.is_locked = True
        self.status = 'locked'
        self.approved_by = user
        import datetime
        from django.utils import timezone
        self.approved_at = timezone.now()
        self.save()

    def unlock(self):
        self.is_locked = False
        self.status = 'draft'
        self.save()

    class Meta:
        ordering = ['-year']
        unique_together = ['church', 'year']


class BudgetIncomeItem(TenantModel):
    """Budget targets for income categories"""
    budget = models.ForeignKey(AnnualBudget, on_delete=models.CASCADE, related_name='income_items')
    category = models.ForeignKey(IncomeCategory, on_delete=models.CASCADE)
    
    # Optional assignment
    department = models.ForeignKey('administration.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='budget_income_items')
    group = models.ForeignKey('groups.Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='budget_income_items')
    section = models.ForeignKey('membership.Section', on_delete=models.SET_NULL, null=True, blank=True, related_name='budget_income_items')
    
    notes = models.TextField(blank=True)

    # Monthly targets
    jan = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # ... (other months)
    feb = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mar = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    apr = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    may = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    jun = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    jul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    aug = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sep = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    oct = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    nov = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    dec = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    @property
    def total(self):
        return sum([self.jan, self.feb, self.mar, self.apr, self.may, self.jun, 
                   self.jul, self.aug, self.sep, self.oct, self.nov, self.dec])
    
    class Meta:
        unique_together = [['budget', 'category'], ['church', 'budget', 'category']]


class BudgetExpenseItem(TenantModel):
    """Budget limits for expense categories"""
    budget = models.ForeignKey(AnnualBudget, on_delete=models.CASCADE, related_name='expense_items')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    
    # Responsible unit
    department = models.ForeignKey('administration.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='budget_expense_items')
    group = models.ForeignKey('groups.Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='budget_expense_items')
    section = models.ForeignKey('membership.Section', on_delete=models.SET_NULL, null=True, blank=True, related_name='budget_expense_items')
    
    notes = models.TextField(blank=True)

    # Monthly limits
    jan = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    feb = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mar = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    apr = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    may = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    jun = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    jul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    aug = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sep = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    oct = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    nov = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    dec = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    @property
    def total(self):
        return sum([self.jan, self.feb, self.mar, self.apr, self.may, self.jun, 
                   self.jul, self.aug, self.sep, self.oct, self.nov, self.dec])

    class Meta:
        unique_together = [['budget', 'category'], ['church', 'budget', 'category']]


class BudgetAuditLog(TenantModel):
    """Audit trail for budget changes"""
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('lock', 'Locked'),
        ('unlock', 'Unlocked'),
    ]
    
    budget = models.ForeignKey(AnnualBudget, on_delete=models.CASCADE, related_name='audit_logs')
    item_type = models.CharField(max_length=10, choices=[('income', 'Income'), ('expense', 'Expense'), ('budget', 'Overall Budget')])
    item_id = models.IntegerField(null=True, blank=True, help_text="ID of the BudgetIncomeItem or BudgetExpenseItem")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    changes = models.JSONField(help_text="JSON representation of what changed")
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

class AssetCategory(TenantModel):
    """Categorization for assets (e.g. Furniture, Equipment, Vehicles)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "Asset Categories"
        unique_together = ['church', 'name']

class Asset(TenantModel):
    """Church Assets with Depreciation"""
    asset_code = models.CharField(max_length=50, blank=True, help_text="Unique Identifier e.g. AST-0001")
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name='assets')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    acquisition_date = models.DateField()
    acquisition_value = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Annual depreciation rate (percentage)
    depreciation_rate = models.DecimalField(
        max_digits=5, decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text="Annual depreciation % (e.g., 20.00 for 5 years life)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.asset_code:
            # simple auto-increment logic
            last = Asset.objects.filter(church=self.church).order_by('-id').first()
            if last and last.asset_code and last.asset_code.startswith('AST-'):
                try:
                    num = int(last.asset_code.split('-')[1])
                    self.asset_code = f"AST-{num + 1:04d}"
                except (IndexError, ValueError):
                    self.asset_code = f"AST-{last.id + 1:04d}"
            else:
                self.asset_code = "AST-0001"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.asset_code} - {self.name}"
        
    @property
    def years_held(self):
        import datetime
        today = datetime.date.today()
        # Simple year diff (approximate) or days/365.25
        delta = today - self.acquisition_date
        years = delta.days / 365.25
        return max(0, years)
        
    @property
    def accumulated_depreciation(self):
        if self.depreciation_rate <= 0:
            return 0
        from decimal import Decimal
        # Value * (Rate/100) * Years
        # Need to handle Decimal/Float types
        years = self.years_held
        initial_val = float(self.acquisition_value)
        rate = float(self.depreciation_rate) / 100.0
        
        dep = initial_val * rate * years
        # Cap at initial value
        return min(initial_val, dep)
        
    @property
    def net_book_value(self):
        initial_val = float(self.acquisition_value)
        dep = self.accumulated_depreciation
        return max(0, initial_val - dep)
    class Meta:
        unique_together = ['church', 'asset_code']
