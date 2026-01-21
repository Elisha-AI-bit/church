from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectFundingViewSet, ProjectAssignmentViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'funding', ProjectFundingViewSet)
router.register(r'assignments', ProjectAssignmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
