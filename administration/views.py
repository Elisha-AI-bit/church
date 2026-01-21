from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import OfficeBearer, ChurchCouncil, LayLeader, ChurchElder, Stewardship
from .serializers import (
    OfficeBearerSerializer, ChurchCouncilSerializer, LayLeaderSerializer,
    ChurchElderSerializer, StewardshipSerializer
)


class OfficeBearerViewSet(viewsets.ModelViewSet):
    queryset = OfficeBearer.objects.select_related('member')
    serializer_class = OfficeBearerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['position', 'is_active']


class ChurchCouncilViewSet(viewsets.ModelViewSet):
    queryset = ChurchCouncil.objects.select_related('member')
    serializer_class = ChurchCouncilSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['member__first_name', 'member__last_name', 'role']
    filterset_fields = ['is_active']


class LayLeaderViewSet(viewsets.ModelViewSet):
    queryset = LayLeader.objects.select_related('member')
    serializer_class = LayLeaderSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['member__first_name', 'member__last_name', 'specialty']
    filterset_fields = ['is_active']


class ChurchElderViewSet(viewsets.ModelViewSet):
    queryset = ChurchElder.objects.select_related('member', 'section')
    serializer_class = ChurchElderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['section', 'is_active']


class StewardshipViewSet(viewsets.ModelViewSet):
    queryset = Stewardship.objects.select_related('member', 'section')
    serializer_class = StewardshipSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'section', 'is_active']
