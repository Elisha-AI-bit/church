from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import SpecialDay, Pledge, Donation, HarvestItem
from .serializers import SpecialDaySerializer, PledgeSerializer, DonationSerializer, HarvestItemSerializer
from finance.models import Income, IncomeCategory, BankAccount
from django.shortcuts import render

def special_events_dashboard(request):
    """Render the special events dashboard"""
    return render(request, 'dashboard/special_events.html')

class SpecialDayViewSet(viewsets.ModelViewSet):
    queryset = SpecialDay.objects.all()
    serializer_class = SpecialDaySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['-date']

    @action(detail=True, methods=['post'])
    def update_items(self, request, pk=None):
        """Bulk update items for this event (Sync items from FE)"""
        event = self.get_object()
        items_data = request.data.get('items', [])
        
        # Get existing IDs to track deletions
        existing_ids = set(event.items.values_list('id', flat=True))
        incoming_ids = set(item.get('id') for item in items_data if item.get('id'))
        
        # Items to delete
        to_delete_ids = existing_ids - incoming_ids
        HarvestItem.objects.filter(id__in=to_delete_ids).delete()
        
        updated_items = []
        
        for item_data in items_data:
            item_id = item_data.get('id')
            status_val = item_data.get('status', 'received')
            sold_amount = item_data.get('sold_amount')
            sold_date = item_data.get('sold_date') or request.data.get('date') # Default to today if not set?
            
            if item_id:
                # Update
                item = HarvestItem.objects.get(id=item_id)
                item.item_name = item_data.get('item_name')
                item.quantity = item_data.get('quantity', 1)
                item.estimated_value = item_data.get('estimated_value', 0)
                item.reserve_price = item_data.get('reserve_price', 0)
                item.donor_name = item_data.get('donor_name', '')
                item.status = status_val
                
                if status_val == 'sold' and sold_amount:
                     item.sold_amount = sold_amount
                     # If newly sold or amount changed, handle finance? 
                     # For simplicity, we assume the specific 'sell' action handled finance, 
                     # but here we might need to sync it. 
                     # Let's call the logic to ensure finance record exists if sold
                     # Reuse logic from HarvestItemViewSet if possible, or duplicate for safety
                     pass 
                
                item.save()
                updated_items.append(item)
            else:
                # Create
                item = HarvestItem.objects.create(
                    event=event,
                    item_name=item_data.get('item_name'),
                    quantity=item_data.get('quantity', 1),
                    estimated_value=item_data.get('estimated_value', 0),
                    reserve_price=item_data.get('reserve_price', 0),
                    donor_name=item_data.get('donor_name', ''),
                    status=status_val,
                    sold_amount=sold_amount if status_val == 'sold' else None
                )
                updated_items.append(item)
                
            # Post-save finance check for this item
            if item.status == 'sold' and item.sold_amount and not item.finance_income:
                 # Create income
                 try:
                    category, _ = IncomeCategory.objects.get_or_create(name="Harvest Sales")
                    default_account = BankAccount.objects.first()
                    if default_account:
                        income = Income.objects.create(
                            category=category,
                            bank_account=default_account,
                            amount=item.sold_amount,
                            transaction_date=item.sold_date or item.created_at.date(),
                            payer_name=f"Sale of {item.item_name}",
                            description=f"Harvest Sale: {item.item_name} from {event.name}",
                            payment_method='cash',
                            created_by=request.user
                        )
                        item.finance_income = income
                        item.save()
                 except Exception as e:
                     print(f"Auto-finance error: {e}")
        
        return Response({'status': 'Items updated', 'count': len(updated_items)})

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    
    def perform_create(self, serializer):
        donation = serializer.save(created_by=self.request.user)
        # Auto-create Finance Income Record
        self._create_finance_record(donation)
        
    def _create_finance_record(self, donation):
        try:
            # Find or Create Category for Special Events
            category, _ = IncomeCategory.objects.get_or_create(name="Special Events")
            default_account = BankAccount.objects.first() # Simplification
            
            if default_account:
                income = Income.objects.create(
                    category=category,
                    bank_account=default_account,
                    amount=donation.amount,
                    transaction_date=donation.date,
                    payer_name=donation.donor_name or (donation.member.full_name if donation.member else "Anonymous"),
                    description=f"Donation for {donation.event.name}",
                    payment_method='cash',
                    created_by=donation.created_by
                )
                donation.finance_income = income
                donation.save()
        except Exception as e:
            print(f"Error linking finance: {e}")

class HarvestItemViewSet(viewsets.ModelViewSet):
    queryset = HarvestItem.objects.all()
    serializer_class = HarvestItemSerializer
    
    def perform_create(self, serializer):
        item = serializer.save()
        if item.status == 'sold' and item.sold_amount:
            self._record_sale_income(item, self.request.user)
            
    def _record_sale_income(self, item, user):
        try:
            category, _ = IncomeCategory.objects.get_or_create(name="Harvest Sales")
            default_account = BankAccount.objects.first()
            
            if default_account and not item.finance_income:
                income = Income.objects.create(
                    category=category,
                    bank_account=default_account,
                    amount=item.sold_amount,
                    transaction_date=item.sold_date or item.created_at.date(),
                    payer_name=f"Sale of {item.item_name}",
                    description=f"Harvest Sale: {item.item_name} from {item.event.name}",
                    payment_method='cash',
                    created_by=user
                )
                item.finance_income = income
                item.save()
        except Exception as e:
            print(f"Error recording income: {e}")

    @action(detail=True, methods=['post'])
    def sell(self, request, pk=None):
        """Sell an item and record income"""
        item = self.get_object()
        amount = request.data.get('amount')
        
        if not amount:
            return Response({'error': 'Amount required'}, status=400)
            
        item.status = 'sold'
        item.sold_amount = amount
        item.sold_date = request.data.get('date')
        item.save()
        
        self._record_sale_income(item, request.user)
            
        return Response({'status': 'Item sold and income recorded'})

class PledgeViewSet(viewsets.ModelViewSet):
    queryset = Pledge.objects.all()
    serializer_class = PledgeSerializer
