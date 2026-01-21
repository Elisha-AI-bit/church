from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventCategoryViewSet, EventViewSet, annual_planner_view, sunday_activities_view, SundayReportViewSet

router = DefaultRouter()
router.register(r'categories', EventCategoryViewSet)
router.register(r'events', EventViewSet)
router.register(r'sunday-reports', SundayReportViewSet)

urlpatterns = [
    path('annual/', annual_planner_view, name='annual_planner'),
    path('sunday-activities/', sunday_activities_view, name='sunday_activities'),
    path('api/', include(router.urls)),
]
