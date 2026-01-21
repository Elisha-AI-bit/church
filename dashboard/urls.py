from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('membership/', views.membership_page, name='membership_page'),
    path('finance/', views.finance_page, name='finance_page'),
    path('groups/', views.groups_page, name='groups_page'),
    path('committees/', views.committees_page, name='committees_page'),
    path('projects/', views.projects_page, name='projects_page'),
    path('reports/', views.reports_page, name='reports_page'),
    path('administration/', views.administration_page, name='administration_page'),
    path('assets/', views.assets_page, name='assets_page'),
]
