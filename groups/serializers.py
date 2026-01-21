from rest_framework import serializers
from .models import Group, GroupLeadership, GroupMembership


class GroupSerializer(serializers.ModelSerializer):
    group_type_display = serializers.CharField(source='get_group_type_display', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    def get_member_count(self, obj):
        return obj.memberships.filter(is_active=True).count()
    
    class Meta:
        model = Group
        fields = '__all__'


class GroupLeadershipSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = GroupLeadership
        fields = '__all__'


class GroupMembershipSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = '__all__'
