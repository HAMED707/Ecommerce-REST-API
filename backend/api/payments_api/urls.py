from django.urls import path
from . import views

urlpatterns = [
    # Payment endpoints
    path('', views.payment_list_view, name='payment-list'),
    path('create/', views.create_payment_view, name='payment-create'),
    path('process/', views.process_payment_view, name='payment-process'),
    
    # Refund endpoints (must be before payment_id to avoid conflict)
    path('refunds/', views.refund_list_view, name='refund-list'),
    path('refunds/create/', views.create_refund_view, name='refund-create'),
    
    # Payment detail/cancel (must be last)
    path('<str:payment_id>/', views.payment_detail_view, name='payment-detail'),
    path('<str:payment_id>/cancel/', views.cancel_payment_view, name='payment-cancel'),
]
