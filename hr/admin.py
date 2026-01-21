from django.contrib import admin
from .models import Employee, PayrollPeriod, Payslip, PayGrade

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'role', 'pay_grade', 'status', 'leave_days_accrued')
    list_filter = ('status', 'role', 'pay_grade')
    search_fields = ('first_name', 'last_name', 'nrc_number')

@admin.register(PayGrade)
class PayGradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_leave_days')

admin.site.register(PayrollPeriod)
admin.site.register(Payslip)
