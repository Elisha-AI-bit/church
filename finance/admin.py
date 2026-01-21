from django.contrib import admin
from .models import (
    BankAccount, IncomeCategory, ExpenseCategory, RemittanceSettings,
    Income, Expense, Remittance, Assessment,
    AnnualBudget, BudgetIncomeItem, BudgetExpenseItem, BudgetAuditLog
)


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['account_name', 'bank_name', 'account_type', 'current_balance', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['account_name', 'bank_name', 'account_number']


@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_remittance', 'is_active']
    list_filter = ['is_remittance', 'is_active']
    search_fields = ['name']


@admin.register(RemittanceSettings)
class RemittanceSettingsAdmin(admin.ModelAdmin):
    list_display = ['remittance_type', 'percentage', 'is_active']
    list_filter = ['remittance_type', 'is_active']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'transaction_date', 'bank_account', 'payment_method', 'remittances_calculated']
    list_filter = ['category', 'payment_method', 'transaction_date', 'remittances_calculated']
    search_fields = ['payer_name', 'receipt_number', 'description']
    date_hierarchy = 'transaction_date'


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'transaction_date', 'bank_account', 'payee_name', 'payment_method']
    list_filter = ['category', 'payment_method', 'transaction_date']
    search_fields = ['payee_name', 'voucher_number', 'description']
    date_hierarchy = 'transaction_date'


@admin.register(Remittance)
class RemittanceAdmin(admin.ModelAdmin):
    list_display = ['remittance_setting', 'income', 'amount', 'percentage_used', 'paid', 'paid_date']
    list_filter = ['remittance_setting', 'paid']
    search_fields = ['income__receipt_number']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['assessment_type', 'amount', 'frequency', 'due_date', 'paid', 'paid_date']
    list_filter = ['assessment_type', 'frequency', 'paid']
    date_hierarchy = 'due_date'


# Budget Management
class BudgetIncomeItemInline(admin.TabularInline):
    model = BudgetIncomeItem
    extra = 0
    fields = ['category', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']


class BudgetExpenseItemInline(admin.TabularInline):
    model = BudgetExpenseItem
    extra = 0
    fields = ['category', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']


@admin.register(AnnualBudget)
class AnnualBudgetAdmin(admin.ModelAdmin):
    list_display = ['year', 'status', 'is_locked', 'approved_by', 'approved_at', 'created_at']
    list_filter = ['status', 'is_locked', 'year']
    inlines = [BudgetIncomeItemInline, BudgetExpenseItemInline]
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_locked:
            return ['year', 'status', 'is_locked', 'approved_by', 'approved_at', 'church']
        return []

@admin.register(BudgetAuditLog)
class BudgetAuditLogAdmin(admin.ModelAdmin):
    list_display = ['budget', 'item_type', 'action', 'user', 'timestamp']
    list_filter = ['item_type', 'action', 'timestamp']
    readonly_fields = ['budget', 'item_type', 'item_id', 'action', 'user', 'changes', 'notes', 'timestamp', 'church']
