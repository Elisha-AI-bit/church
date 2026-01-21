from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from decimal import Decimal
from .models import (
    BankAccount, IncomeCategory, ExpenseCategory, RemittanceSettings,
    BankAccount, IncomeCategory, ExpenseCategory, RemittanceSettings,
    Income, Expense, Remittance, Assessment, AnnualBudget, BudgetIncomeItem, BudgetExpenseItem,
    Asset, AssetCategory, BudgetAuditLog
)
from .serializers import (
    BankAccountSerializer, IncomeCategorySerializer, ExpenseCategorySerializer,
    RemittanceSettingsSerializer, IncomeSerializer, IncomeListSerializer,
    ExpenseSerializer, ExpenseListSerializer, RemittanceSerializer, AssessmentSerializer,
    AnnualBudgetSerializer, BudgetIncomeItemSerializer, BudgetExpenseItemSerializer,
    AssetSerializer, AssetCategorySerializer
)
from django.shortcuts import render

def budget_dashboard_view(request):
    """Render the budget dashboard"""
    return render(request, 'dashboard/budget.html')


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['account_name', 'bank_name']
    filterset_fields = ['account_type', 'is_active']


class IncomeCategoryViewSet(viewsets.ModelViewSet):
    queryset = IncomeCategory.objects.all()
    serializer_class = IncomeCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['is_remittance']


class RemittanceSettingsViewSet(viewsets.ModelViewSet):
    queryset = RemittanceSettings.objects.all()
    serializer_class = RemittanceSettingsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['remittance_type', 'is_active']


class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.select_related('category', 'bank_account', 'created_by').prefetch_related('remittances')
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['payer_name', 'receipt_number', 'description']
    filterset_fields = ['category', 'bank_account', 'payment_method', 'transaction_date']
    ordering_fields = ['transaction_date', 'amount']
    ordering = ['-transaction_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return IncomeListSerializer
        return IncomeSerializer
    
    def perform_create(self, serializer):
        income = serializer.save(created_by=self.request.user)
       # Auto-calculate remittances
        self._calculate_remittances(income)
    
    def _calculate_remittances(self, income):
        """Calculate and create remittances for the income"""
        # Get all active remittance settings applicable to this income category
        applicable_settings = RemittanceSettings.objects.filter(
            is_active=True,
            applicable_to_categories=income.category
        )
        
        for setting in applicable_settings:
            remittance_amount = (income.amount * setting.percentage) / Decimal('100')
            Remittance.objects.create(
                income=income,
                remittance_setting=setting,
                amount=remittance_amount,
                percentage_used=setting.percentage
            )
        
        income.remittances_calculated = True
        income.save()
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get income summary"""
        total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or 0
        return Response({
            'total_income': total_income,
            'by_category': Income.objects.values('category__name').annotate(total=Sum('amount'))
        })


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related('category', 'bank_account', 'created_by', 'related_income')
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['payee_name', 'voucher_number', 'description']
    filterset_fields = ['category', 'bank_account', 'payment_method', 'transaction_date']
    ordering_fields = ['transaction_date', 'amount']
    ordering = ['-transaction_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExpenseListSerializer
        return ExpenseSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get expense summary"""
        total_expense = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        return Response({
            'total_expense': total_expense,
            'by_category': Expense.objects.values('category__name').annotate(total=Sum('amount'))
        })


class RemittanceViewSet(viewsets.ModelViewSet):
    queryset = Remittance.objects.select_related('income', 'remittance_setting', 'expense')
    serializer_class = RemittanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['remittance_setting', 'paid']
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark remittance as paid"""
        remittance = self.get_object()
        paid_date = request.data.get('paid_date')
        
        if not paid_date:
            return Response({'error': 'paid_date is required'}, status=400)
        
        remittance.paid = True
        remittance.paid_date = paid_date
        remittance.save()
        
        return Response({'status': 'Remittance marked as paid'})
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get remittance summary"""
        total_remit = Remittance.objects.aggregate(total=Sum('amount'))['total'] or 0
        paid_remit = Remittance.objects.filter(paid=True).aggregate(total=Sum('amount'))['total'] or 0
        unpaid_remit = Remittance.objects.filter(paid=False).aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'total_remittances': total_remit,
            'paid_remittances': paid_remit,
            'unpaid_remittances': unpaid_remit,
            'by_type': Remittance.objects.values('remittance_setting__remittance_type').annotate(total=Sum('amount'))
        })


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.select_related('expense')
    serializer_class = AssessmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assessment_type', 'frequency', 'paid']
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark assessment as paid"""
        assessment = self.get_object()
        paid_date = request.data.get('paid_date')
        
        if not paid_date:
            return Response({'error': 'paid_date is required'}, status=400)
        
        assessment.paid = True
        assessment.paid_date = paid_date
        assessment.save()
        
        return Response({'status': 'Assessment marked as paid'})


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = AnnualBudget.objects.prefetch_related('income_items', 'expense_items')
    serializer_class = AnnualBudgetSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['-year']
    
    def perform_create(self, serializer):
        # Set the church from the logged-in user
        serializer.save(church=self.request.user.profile.church)

    def create(self, request, *args, **kwargs):
        # Override create to auto-populate items based on existing categories
        year = request.data.get('year')
        if AnnualBudget.objects.filter(year=year).exists():
            return Response({'error': f'Budget for {year} already exists'}, status=400)
            
        response = super().create(request, *args, **kwargs)
        budget_id = response.data['id']
        budget = AnnualBudget.objects.get(id=budget_id)
        
        # Populate Income Items
        from .models import IncomeCategory, ExpenseCategory
        church = budget.church
        for category in IncomeCategory.objects.filter(is_active=True):
            BudgetIncomeItem.objects.get_or_create(
                budget=budget, 
                category=category, 
                church=church
            )
            
        # Populate Expense Items
        for category in ExpenseCategory.objects.filter(is_active=True):
            BudgetExpenseItem.objects.get_or_create(
                budget=budget, 
                category=category, 
                church=church
            )
            
        # Refetch to get nested data
        serializer = self.get_serializer(budget)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """Lock the budget for approval"""
        budget = self.get_object()
        budget.lock(request.user)
        self._log_audit(budget, 'budget', budget.id, 'lock', request.user, {'status': 'locked'})
        return Response(self.get_serializer(budget).data)

    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Unlock the budget for edits"""
        budget = self.get_object()
        budget.unlock()
        self._log_audit(budget, 'budget', budget.id, 'unlock', request.user, {'status': 'draft'})
        return Response(self.get_serializer(budget).data)

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Analyze budget vs actual performance and burn rates"""
        budget = self.get_object()
        month = request.query_params.get('month') # 1-12
        
        income_items = budget.income_items.all()
        expense_items = budget.expense_items.all()
        
        # Calculate actuals (simplified for now, ideally links to Income/Expense tables)
        # Note: Actual expenditure capture is a future enhancement per requirements
        # but we can return the structure for it.
        
        perf_data = {
            'income': [],
            'expense': []
        }
        
        for item in income_items:
            perf_data['income'].append({
                'category': item.category.name,
                'budgeted': item.total,
                # 'actual': ...
            })
            
        for item in expense_items:
            perf_data['expense'].append({
                'category': item.category.name,
                'budgeted': item.total,
                'department': item.department.name if item.department else None,
                # 'actual': ...
            })
            
        return Response(perf_data)

    @action(detail=True, methods=['post'])
    def update_item(self, request, pk=None):
        """Update a specific line item (income or expense) with locking and audit check"""
        budget = self.get_object()
        if budget.is_locked:
            return Response({'error': 'Budget is locked and cannot be edited'}, status=403)

        item_type = request.data.get('type') # 'income' or 'expense'
        item_id = request.data.get('id')
        
        if item_type == 'income':
            model = BudgetIncomeItem
            serializer_cls = BudgetIncomeItemSerializer
        elif item_type == 'expense':
            model = BudgetExpenseItem
            serializer_cls = BudgetExpenseItemSerializer
        else:
            return Response({'error': 'Invalid type'}, status=400)
            
        try:
            item = model.objects.get(id=item_id, budget_id=pk)
            old_values = {}
            for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']:
                old_values[month] = float(getattr(item, month))

            # Update monthly fields
            changes = {}
            for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']:
                if month in request.data:
                    new_val = float(request.data[month])
                    if new_val != old_values[month]:
                        setattr(item, month, new_val)
                        changes[month] = {'old': old_values[month], 'new': new_val}
            
            # Update unit and notes
            if 'notes' in request.data:
                item.notes = request.data['notes']
            if 'department_id' in request.data:
                item.department_id = request.data['department_id']
                
            item.save()
            
            if changes:
                BudgetAuditLog.objects.create(
                    budget=budget,
                    church=budget.church,
                    item_type=item_type,
                    item_id=item.id,
                    action='update',
                    user=request.user,
                    changes=changes,
                    notes=request.data.get('notes', '')
                )
                
            return Response(serializer_cls(item).data)
        except model.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)

    def _log_audit(self, budget, item_type, item_id, action, user, changes, notes=''):
        BudgetAuditLog.objects.create(
            budget=budget,
            church=budget.church,
            item_type=item_type,
            item_id=item_id,
            action=action,
            user=user,
            changes=changes,
            notes=notes
        )

    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """Import budget items from CSV, supporting offline creation"""
        import csv
        import io
        from decimal import Decimal
        from django.db import transaction

        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)

        church = request.user.profile.church
        
        try:
            decoded_file = file.read().decode('utf-8-sig') # Handle potential BOM
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            imported_count = 0
            errors = []
            
            months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

            with transaction.atomic():
                for index, row in enumerate(reader):
                    try:
                        year = int(row.get('Year'))
                        item_type = row.get('Type', '').lower() # 'income' or 'expense'
                        category_name = row.get('Category')
                        
                        if not category_name:
                            continue

                        # Get or create budget for this church
                        budget, created = AnnualBudget.objects.get_or_create(
                            year=year, 
                            church=church,
                            defaults={'status': 'draft', 'is_locked': False}
                        )

                        if budget.is_locked:
                            errors.append(f"Row {index + 1}: Budget for {year} is locked")
                            continue
                        
                        # Use get_or_create with church context
                        if item_type == 'income':
                            category = IncomeCategory.objects.get(name__iexact=category_name, is_active=True)
                            item, _ = BudgetIncomeItem.objects.get_or_create(budget=budget, category=category, church=church)
                        elif item_type == 'expense':
                            category = ExpenseCategory.objects.get(name__iexact=category_name, is_active=True)
                            item, _ = BudgetExpenseItem.objects.get_or_create(budget=budget, category=category, church=church)
                        else:
                            errors.append(f"Row {index + 1}: Invalid type '{item_type}'")
                            continue

                        # Update monthly values
                        for month in months:
                            val = row.get(month.capitalize(), row.get(month, '0'))
                            try:
                                setattr(item, month, Decimal(str(val or 0).replace(',', '')))
                            except:
                                setattr(item, month, Decimal('0'))
                        
                        item.save()
                        imported_count += 1

                    except (IncomeCategory.DoesNotExist, ExpenseCategory.DoesNotExist):
                        errors.append(f"Row {index + 1}: Category '{category_name}' not found or inactive")
                    except Exception as e:
                        errors.append(f"Row {index + 1}: {str(e)}")

            # Log the bulk operation
            if imported_count > 0:
                first_row_year = reader.fieldnames and reader.fieldnames[0] # Just a placeholder
                # We don't have a single budget PK if multiple years are in CSV, 
                # but usually it's one year. We'll skip detailed item audit for bulk imports 
                # to avoid performance issues, or just log the event.
                pass

            return Response({
                'status': 'Import complete',
                'imported': imported_count,
                'errors': errors
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

class AssetCategoryViewSet(viewsets.ModelViewSet):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related('category')
    serializer_class = AssetSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'asset_code', 'description']
    filterset_fields = ['category']
    ordering_fields = ['acquisition_date', 'acquisition_value']
    ordering = ['-acquisition_date']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get asset valuation summary"""
        assets = Asset.objects.all()
        # Calculate totals in python since properties are computed
        total_original_value = sum(a.acquisition_value for a in assets)
        total_net_value = sum(a.net_book_value for a in assets)
        
        return Response({
            'count': assets.count(),
            'total_original_value': total_original_value,
            'total_net_value': total_net_value
        })
