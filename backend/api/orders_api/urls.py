from django.urls import path
from . import views

urlpatterns = [
    # Orders
    path('create/', views.create_order, name='create_order'),
    path('', views.list_orders, name='list_orders'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('number/<str:order_number>/', views.order_by_number, name='order_by_number'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    
    # Shipping Addresses
    path('shipping-addresses/', views.shipping_address_list, name='shipping-address-list'),
    path('shipping-addresses/<int:address_id>/', views.shipping_address_detail, name='shipping-address-detail'),
    path('shipping-addresses/<int:address_id>/set-default/', views.set_default_address, name='set-default-address'),
    path('shipping-addresses/default/', views.get_default_address, name='get-default-address'),
]
