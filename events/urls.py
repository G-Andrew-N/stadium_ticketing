from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.event_list, name='event_list'),
    path('calendar/', views.event_calendar, name='event_calendar'),
    path('create/', views.event_form, name='event_create'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('<int:pk>/edit/', views.event_form, name='event_edit'),
    path('<int:pk>/delete/', views.event_confirm_delete, name='event_confirm_delete'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
]