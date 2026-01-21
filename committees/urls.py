from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommitteeViewSet, CommitteeLeadershipViewSet, CommitteeMembershipViewSet

router = DefaultRouter()
router.register(r'committees', CommitteeViewSet)
router.register(r'leadership', CommitteeLeadershipViewSet)
router.register(r'membership', CommitteeMembershipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
