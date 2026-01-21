from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (EmployeeViewSet, PayrollViewSet, PayslipViewSet, 
                    employee_list_view, payroll_dashboard_view,
                    payroll_report_view, payslip_view)

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'payroll', PayrollViewSet)
router.register(r'payslips', PayslipViewSet)

urlpatterns = [
    path('employees/dashboard/', employee_list_view, name='hr_employees'),
    path('payroll/dashboard/', payroll_dashboard_view, name='hr_payroll'),
    path('payroll/<int:period_id>/report/', payroll_report_view, name='payroll_report'),
    path('payslip/<int:payslip_id>/', payslip_view, name='payslip_detail'),
    path('', include(router.urls)),
]
