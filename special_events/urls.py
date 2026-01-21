from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (SpecialDayViewSet, DonationViewSet, HarvestItemViewSet, 
                    PledgeViewSet, special_events_dashboard)

router = DefaultRouter()
router.register(r'events', SpecialDayViewSet)
router.register(r'donations', DonationViewSet)
router.register(r'items', HarvestItemViewSet)
router.register(r'pledges', PledgeViewSet)

urlpatterns = [
    path('dashboard/', special_events_dashboard, name='special_events_dashboard'),
    path('api/', include(router.urls)),
]
