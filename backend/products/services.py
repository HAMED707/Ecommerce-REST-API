from .models import Product
from django.db.models import Q


class ProductService:
    """Business logic for products"""
    
    @staticmethod
    def get_all_products():
        """Get all products"""
        return Product.objects.all()
    
    @staticmethod
    def get_product_by_id(product_id):
        """Get single product by ID"""
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None
    
    @staticmethod
    def search_products(query):
        """Search products by name or description"""
        # TODO: add elasticsearch for better search?
        return Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    @staticmethod
    def filter_by_category(category):
        """Filter products by category"""
        return Product.objects.filter(category=category)
    
    @staticmethod
    def filter_by_price(min_price, max_price):
        """Filter products by price range"""
        return Product.objects.filter(price__gte=min_price, price__lte=max_price)
    
    @staticmethod
    def get_featured_products():
        """Get featured products"""
        # grab the first 8 active products
        return Product.objects.filter(is_active=True)[:8]
