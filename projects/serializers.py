from rest_framework import serializers
from .models import Project, ProjectFunding, ProjectAssignment


class ProjectFundingSerializer(serializers.ModelSerializer):
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    
    class Meta:
        model = ProjectFunding
        fields = '__all__'


class ProjectAssignmentSerializer(serializers.ModelSerializer):
    responsible_entity_type_display = serializers.CharField(source='get_responsible_entity_type_display', read_only=True)
    
    class Meta:
        model = ProjectAssignment
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    funding_type_display = serializers.CharField(source='get_funding_type_display', read_only=True)
    remaining_budget = serializers.ReadOnlyField()
    budget_utilization_percentage = serializers.ReadOnlyField()
    funding_sources = ProjectFundingSerializer(many=True, read_only=True)
    assignments = ProjectAssignmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'


class ProjectListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    remaining_budget = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'status', 'status_display', 'total_budget', 'spent_amount', 'remaining_budget', 'start_date']
