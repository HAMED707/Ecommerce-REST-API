from django.urls import path
from .views import (
    get_cart,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    clear_cart,
    cart_count
)

urlpatterns = [
    path('', get_cart, name='cart-detail'),
    path('add/', add_to_cart, name='add-to-cart'),
    path('count/', cart_count, name='cart-count'),
    path('items/<int:product_id>/', update_cart_item, name='update-cart-item'),
    path('items/<int:product_id>/remove/', remove_from_cart, name='remove-from-cart'),
    path('clear/', clear_cart, name='clear-cart'),
]
