from rest_framework import serializers
from .models import (
    BankAccount, IncomeCategory, ExpenseCategory, RemittanceSettings,
    Income, Expense, Remittance, Assessment, AnnualBudget, BudgetIncomeItem, BudgetExpenseItem,
    Asset, AssetCategory, BudgetAuditLog
)

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'

class IncomeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeCategory
        fields = '__all__'

class ExpenseCategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True)
    
    class Meta:
        model = ExpenseCategory
        fields = '__all__'

class RemittanceSettingsSerializer(serializers.ModelSerializer):
    remittance_type_display = serializers.CharField(source='get_remittance_type_display', read_only=True)
    class Meta:
        model = RemittanceSettings
        fields = '__all__'

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = '__all__'
        read_only_fields = ['created_by', 'remittances_calculated']

class IncomeListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    bank_account_name = serializers.CharField(source='bank_account.bank_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Income
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['created_by']

class ExpenseListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    bank_account_name = serializers.CharField(source='bank_account.bank_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Expense
        fields = '__all__'

class RemittanceSerializer(serializers.ModelSerializer):
    income_details = IncomeListSerializer(source='income', read_only=True)
    setting_details = RemittanceSettingsSerializer(source='remittance_setting', read_only=True)
    
    class Meta:
        model = Remittance
        fields = '__all__'

class AssessmentSerializer(serializers.ModelSerializer):
    assessment_type_display = serializers.CharField(source='get_assessment_type_display', read_only=True)
    
    class Meta:
        model = Assessment
        fields = '__all__'

class BudgetIncomeItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    total = serializers.ReadOnlyField()
    
    class Meta:
        model = BudgetIncomeItem
        fields = '__all__'

class BudgetExpenseItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.expense_type', read_only=True) # OPEX/CAPEX
    category_group = serializers.CharField(source='category.category_type', read_only=True) # PE/Admin/etc
    department_name = serializers.CharField(source='department.name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    total = serializers.ReadOnlyField()
    
    class Meta:
        model = BudgetExpenseItem
        fields = '__all__'

class BudgetAuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = BudgetAuditLog
        fields = '__all__'

class AnnualBudgetSerializer(serializers.ModelSerializer):
    income_items = BudgetIncomeItemSerializer(many=True, read_only=True)
    expense_items = BudgetExpenseItemSerializer(many=True, read_only=True)
    audit_logs = BudgetAuditLogSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_income = serializers.SerializerMethodField()
    total_expense = serializers.SerializerMethodField()
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = AnnualBudget
        fields = '__all__'
        
    def get_total_income(self, obj):
        return sum(item.total for item in obj.income_items.all())

    def get_total_expense(self, obj):
        return sum(item.total for item in obj.expense_items.all())

class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = '__all__'

class AssetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    asset_code = serializers.CharField(read_only=True) # Auto-generated
    accumulated_depreciation = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    net_book_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    years_held = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Asset
        fields = '__all__'
