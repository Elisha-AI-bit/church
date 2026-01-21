from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Committee, CommitteeLeadership, CommitteeMembership
from .serializers import CommitteeSerializer, CommitteeLeadershipSerializer, CommitteeMembershipSerializer


class CommitteeViewSet(viewsets.ModelViewSet):
    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']


class CommitteeLeadershipViewSet(viewsets.ModelViewSet):
    queryset = CommitteeLeadership.objects.select_related('committee', 'member')
    serializer_class = CommitteeLeadershipSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['committee', 'role', 'is_active']


class CommitteeMembershipViewSet(viewsets.ModelViewSet):
    queryset = CommitteeMembership.objects.select_related('committee', 'member')
    serializer_class = CommitteeMembershipSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['committee', 'is_active']
