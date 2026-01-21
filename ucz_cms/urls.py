"""
URL configuration for UCZ Church Management System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', include('dashboard.urls')),
    
    # API endpoints
    path('api/membership/', include('membership.urls')),
    path('api/administration/', include('administration.urls')),
    path('api/groups/', include('groups.urls')),
    path('api/committees/', include('committees.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/finance/', include('finance.urls')),
    path('api/hr/', include('hr.urls')),
    path('api/reports/', include('reports.urls')),
    path('planner/', include('planner.urls')),
    path('special/', include('special_events.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
