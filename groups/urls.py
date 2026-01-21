from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupViewSet, GroupLeadershipViewSet, GroupMembershipViewSet

router = DefaultRouter()
router.register(r'groups', GroupViewSet)
router.register(r'leadership', GroupLeadershipViewSet)
router.register(r'membership', GroupMembershipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
