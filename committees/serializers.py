from rest_framework import serializers
from .models import Committee, CommitteeLeadership, CommitteeMembership


class CommitteeSerializer(serializers.ModelSerializer):
    committee_type_display = serializers.CharField(source='get_committee_type_display', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    def get_member_count(self, obj):
        return obj.memberships.filter(is_active=True).count()
    
    class Meta:
        model = Committee
        fields = '__all__'


class CommitteeLeadershipSerializer(serializers.ModelSerializer):
    committee_name = serializers.CharField(source='committee.name', read_only=True)
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = CommitteeLeadership
        fields = '__all__'


class CommitteeMembershipSerializer(serializers.ModelSerializer):
    committee_name = serializers.CharField(source='committee.name', read_only=True)
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    
    class Meta:
        model = CommitteeMembership
        fields = '__all__'
