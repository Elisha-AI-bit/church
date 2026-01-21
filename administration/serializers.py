from rest_framework import serializers
from .models import OfficeBearer, ChurchCouncil, LayLeader, ChurchElder, Stewardship


class OfficeBearerSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    
    class Meta:
        model = OfficeBearer
        fields = '__all__'


class ChurchCouncilSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    
    class Meta:
        model = ChurchCouncil
        fields = '__all__'


class LayLeaderSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    
    class Meta:
        model = LayLeader
        fields = '__all__'


class ChurchElderSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    
    class Meta:
        model = ChurchElder
        fields = '__all__'


class StewardshipSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = Stewardship
        fields = '__all__'
