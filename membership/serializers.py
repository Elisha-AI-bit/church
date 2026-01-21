from rest_framework import serializers
from .models import Section, Position, Member, Dependent, PositionHistory, MemberTransfer


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class DependentSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Dependent
        fields = '__all__'


class PositionHistorySerializer(serializers.ModelSerializer):
    position_name = serializers.CharField(source='position.title', read_only=True)
    
    class Meta:
        model = PositionHistory
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    dependents = DependentSerializer(many=True, required=False)
    position_history = PositionHistorySerializer(many=True, read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    position_names = serializers.SerializerMethodField()
    
    def get_position_names(self, obj):
        return ", ".join([p.title for p in obj.current_positions.all()])
    
    class Meta:
        model = Member
        fields = '__all__'
        read_only_fields = ['membership_number']
        
    def create(self, validated_data):
        dependents_data = validated_data.pop('dependents', [])
        current_positions = validated_data.pop('current_positions', [])
        member = Member.objects.create(**validated_data)
        
        if current_positions:
            member.current_positions.set(current_positions)
            
        for dependent_data in dependents_data:
            Dependent.objects.create(principal_member=member, **dependent_data)
            
        return member


class MemberListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    section_name = serializers.CharField(source='section.name', read_only=True)
    position_names = serializers.SerializerMethodField()
    
    def get_position_names(self, obj):
        return ", ".join([p.title for p in obj.current_positions.all()])
    
    class Meta:
        model = Member
        fields = ['id', 'membership_number', 'full_name', 'gender', 'age', 'section_name', 'membership_status', 'position_names', 'phone', 'email']


class MemberTransferSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    
    class Meta:
        model = MemberTransfer
        fields = '__all__'
