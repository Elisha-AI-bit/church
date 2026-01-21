from rest_framework import serializers
from .models import Employee, PayrollPeriod, Payslip

class EmployeeSerializer(serializers.ModelSerializer):
    pay_grade_name = serializers.CharField(source='pay_grade.name', read_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'

class PayslipSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    leave_days_balance = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    leave_pay_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Payslip
        fields = '__all__'

class PayrollPeriodSerializer(serializers.ModelSerializer):
    total_staff = serializers.SerializerMethodField()
    total_payout = serializers.ReadOnlyField()
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    
    class Meta:
        model = PayrollPeriod
        fields = '__all__'
        
    def get_total_staff(self, obj):
        return obj.payslips.count()
