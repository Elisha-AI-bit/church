from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BankAccountViewSet, IncomeCategoryViewSet, ExpenseCategoryViewSet,
    RemittanceSettingsViewSet, IncomeViewSet, ExpenseViewSet,
    RemittanceViewSet, AssessmentViewSet, BudgetViewSet, budget_dashboard_view,
    AssetViewSet, AssetCategoryViewSet
)

router = DefaultRouter()
router.register(r'bank-accounts', BankAccountViewSet)
router.register(r'income-categories', IncomeCategoryViewSet)
router.register(r'expense-categories', ExpenseCategoryViewSet)
router.register(r'remittance-settings', RemittanceSettingsViewSet)
router.register(r'income', IncomeViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'remittances', RemittanceViewSet)
router.register(r'assessments', AssessmentViewSet)
router.register(r'budgets', BudgetViewSet)
router.register(r'assets', AssetViewSet)
router.register(r'asset-categories', AssetCategoryViewSet)

urlpatterns = [
    path('budget/', budget_dashboard_view, name='budget_dashboard'),
    path('', include(router.urls)),
]
