from django.urls import path
from . import views

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('purchase/<int:event_id>/<int:tickettype_id>/', views.ticket_purchase, name='ticket_purchase'),  # <-- fixed argument name
    path('confirm/<int:pk>/', views.ticket_confirm, name='ticket_confirm'),
    path('cancel/<int:pk>/', views.ticket_cancel, name='ticket_cancel'),
    #path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
]