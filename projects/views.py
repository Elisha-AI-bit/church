from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, ProjectFunding, ProjectAssignment
from .serializers import (
    ProjectSerializer, ProjectListSerializer,
    ProjectFundingSerializer, ProjectAssignmentSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.prefetch_related('funding_sources', 'assignments')
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['status', 'funding_type']
    ordering_fields = ['created_at', 'start_date', 'total_budget']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer


class ProjectFundingViewSet(viewsets.ModelViewSet):
    queryset = ProjectFunding.objects.select_related('project')
    serializer_class = ProjectFundingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'source_type']


class ProjectAssignmentViewSet(viewsets.ModelViewSet):
    queryset = ProjectAssignment.objects.select_related('project')
    serializer_class = ProjectAssignmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'responsible_entity_type']
