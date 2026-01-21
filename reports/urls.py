from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportTemplateViewSet, SavedReportViewSet, ReportViewSet

router = DefaultRouter()
router.register(r'templates', ReportTemplateViewSet)
router.register(r'saved', SavedReportViewSet)
router.register(r'generate', ReportViewSet, basename='generate')

urlpatterns = [
    path('', include(router.urls)),
]
