from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OfficeBearerViewSet, ChurchCouncilViewSet, LayLeaderViewSet,
    ChurchElderViewSet, StewardshipViewSet
)

router = DefaultRouter()
router.register(r'office-bearers', OfficeBearerViewSet)
router.register(r'council', ChurchCouncilViewSet)
router.register(r'lay-leaders', LayLeaderViewSet)
router.register(r'elders', ChurchElderViewSet)
router.register(r'stewardship', StewardshipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
