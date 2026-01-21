from rest_framework import serializers
from .models import ReportTemplate, SavedReport


class ReportTemplateSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = '__all__'


class SavedReportSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.username', read_only=True)
    
    class Meta:
        model = SavedReport
        fields = '__all__'
