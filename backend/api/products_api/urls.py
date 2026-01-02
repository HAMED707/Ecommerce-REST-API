from django.urls import path
from .views import (
    product_list,
    product_detail,
    featured_products,
    add_review,
    product_reviews
)

urlpatterns = [
    path('', product_list, name='product-list'),
    path('<int:product_id>/', product_detail, name='product-detail'),
    path('featured/', featured_products, name='featured-products'),
    path('<int:product_id>/reviews/', product_reviews, name='product-reviews'),
    path('<int:product_id>/reviews/add/', add_review, name='add-review'),
]
