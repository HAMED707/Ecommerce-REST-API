from django.urls import path, include

urlpatterns = [
    path("auth/", include('api.accounts_api.urls')),
    path("products/", include('api.products_api.urls')),
    path("cart/", include('api.cart_api.urls')),
    path("orders/", include('api.orders_api.urls')),
    path("payments/", include('api.payments_api.urls')),  
]