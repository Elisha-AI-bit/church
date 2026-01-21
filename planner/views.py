from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from .models import Event, EventCategory, SundayReport, SectionFunds, SundayItem
from .serializers import EventSerializer, EventCategorySerializer, SundayReportSerializer, SectionFundsSerializer, SundayItemSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from membership.models import Section

def sunday_activities_view(request):
    """Render the Sunday activities dashboard"""
    return render(request, 'dashboard/sunday_activities.html')

def annual_planner_view(request):
    """Render the annual planner dashboard"""
    return render(request, 'dashboard/planner.html')

class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    filterset_fields = ['category', 'status', 'start_date']
    ordering_fields = ['start_date', 'budget_estimated']
    ordering = ['start_date']

class SundayReportViewSet(viewsets.ModelViewSet):
    queryset = SundayReport.objects.prefetch_related('section_funds')
    serializer_class = SundayReportSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['-date']
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get or create report for nearest Sunday or today"""
        # For simplicity, let's just return the latest or allow creating for a date on frontend
        latest = SundayReport.objects.order_by('-date').first()
        if latest:
            serializer = self.get_serializer(latest)
            return Response(serializer.data)
        return Response({})

    @action(detail=True, methods=['post'])
    def update_funds(self, request, pk=None):
        """Update section funds for this report"""
        report = self.get_object()
        funds_data = request.data.get('funds', []) # List of {section_id, tithe, envelopes...}
        
        with transaction.atomic():
            for item in funds_data:
                section_id = item.get('section_id')
                SectionFunds.objects.update_or_create(
                    report=report,
                    section_id=section_id,
                    defaults={
                        'tithe_amount': item.get('tithe', 0),
                        'envelopes_amount': item.get('envelopes', 0),
                        'loose_offering_amount': item.get('loose', 0),
                        'thanksgiving_amount': item.get('thanksgiving', 0),
                    }
                )
            
            # Recalculate totals
            total_offering = sum(f.envelopes_amount + f.loose_offering_amount + f.thanksgiving_amount for f in report.section_funds.all())
            total_tithe = sum(f.tithe_amount for f in report.section_funds.all())
            
            report.total_offering = total_offering
            report.total_tithe = total_tithe
            report.save()
            
        return Response(self.get_serializer(report).data)

    @action(detail=True, methods=['post'])
    def update_items(self, request, pk=None):
        """Update donated items for this report"""
        report = self.get_object()
        items_data = request.data.get('items', [])
        
        with transaction.atomic():
            # Clear existing items? Or update? Let's clear and re-add for simplicity of the UI form
            # But maybe risky if ID based.
            # Strategy: Delete all for this report and recreate. 
            # Ideally we should use IDs to update, but for this specific "save functionality" from UI, replace is easiest.
            report.items.all().delete()
            
            for item in items_data:
                SundayItem.objects.create(
                    report=report,
                    item_name=item.get('item_name'),
                    quantity=item.get('quantity', 1),
                    estimated_value=item.get('estimated_value', 0),
                    reserve_price=item.get('reserve_price', 0),
                    status=item.get('status', 'pending'),
                    sold_price=item.get('sold_price', 0) if item.get('status') == 'sold' else 0
                )
            
            # Recalculate total sales
            total_sales = sum(i.sold_price for i in report.items.all() if i.status == 'sold')
            report.total_items_sale = total_sales
            report.save()
            
        return Response(self.get_serializer(report).data)
