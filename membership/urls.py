from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SectionViewSet, PositionViewSet, MemberViewSet,
    DependentViewSet, PositionHistoryViewSet, MemberTransferViewSet
)

router = DefaultRouter()
router.register(r'sections', SectionViewSet)
router.register(r'positions', PositionViewSet)
router.register(r'members', MemberViewSet)
router.register(r'dependents', DependentViewSet)
router.register(r'position-history', PositionHistoryViewSet)
router.register(r'transfers', MemberTransferViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
