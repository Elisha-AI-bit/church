from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Group, GroupLeadership, GroupMembership
from .serializers import GroupSerializer, GroupLeadershipSerializer, GroupMembershipSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']


class GroupLeadershipViewSet(viewsets.ModelViewSet):
    queryset = GroupLeadership.objects.select_related('group', 'member')
    serializer_class = GroupLeadershipSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group', 'role', 'is_active']


class GroupMembershipViewSet(viewsets.ModelViewSet):
    queryset = GroupMembership.objects.select_related('group', 'member')
    serializer_class = GroupMembershipSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group', 'is_active']
