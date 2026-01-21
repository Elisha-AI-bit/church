from rest_framework import serializers
from .models import Event, EventCategory

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    
    class Meta:
        model = Event
        fields = '__all__'

from .models import SundayReport, SectionFunds, SundayItem

class SundayItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SundayItem
        fields = '__all__'
        read_only_fields = ['report']

class SectionFundsSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField(source='section.name', read_only=True)
    total_amount = serializers.ReadOnlyField(source='total')
    
    class Meta:
        model = SectionFunds
        fields = '__all__'
        read_only_fields = ['report']

class SundayReportSerializer(serializers.ModelSerializer):
    section_on_duty_name = serializers.CharField(source='section_on_duty.name', read_only=True, allow_null=True)
    funds_breakdown = SectionFundsSerializer(source='section_funds', many=True, read_only=True)
    items_list = SundayItemSerializer(source='items', many=True, read_only=True)
    grand_total = serializers.ReadOnlyField()
    
    class Meta:
        model = SundayReport
        fields = '__all__'
