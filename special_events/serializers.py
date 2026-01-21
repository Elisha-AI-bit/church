from rest_framework import serializers
from .models import SpecialDay, Pledge, Donation, HarvestItem

class SpecialDaySerializer(serializers.ModelSerializer):
    total_cash = serializers.SerializerMethodField()
    total_pledged = serializers.SerializerMethodField()
    total_items_value = serializers.SerializerMethodField()
    total_sales = serializers.SerializerMethodField()
    total_estimated_unsold = serializers.SerializerMethodField()
    
    class Meta:
        model = SpecialDay
        fields = '__all__'
        
    def get_total_cash(self, obj):
        return sum(d.amount for d in obj.donations.all())
        
    def get_total_pledged(self, obj):
        return sum(p.amount for p in obj.pledges.all())
        
    def get_total_items_value(self, obj):
        # Value of items (Estimated if not sold, Sold Amount if sold)
        total = 0
        for item in obj.items.all():
            if item.status == 'sold' and item.sold_amount:
                total += item.sold_amount
            else:
                total += item.estimated_value
        return total

    def get_total_sales(self, obj):
        return sum(item.sold_amount for item in obj.items.filter(status='sold') if item.sold_amount)

    def get_total_estimated_unsold(self, obj):
        return sum(item.estimated_value for item in obj.items.exclude(status='sold'))

class PledgeSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    class Meta:
        model = Pledge
        fields = '__all__'

class DonationSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    class Meta:
        model = Donation
        fields = '__all__'

class HarvestItemSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    class Meta:
        model = HarvestItem
        fields = '__all__'
