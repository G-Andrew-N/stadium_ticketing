from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('password_change/', views.password_change, name='password_change'),
    path('password/reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password/reset/complete/', views.password_reset_complete, name='password_reset_complete'),
]