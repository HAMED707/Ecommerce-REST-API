from .models import Cart, CartItem
from products.models import Product
from django.shortcuts import get_object_or_404


class CartService:
    """Business logic for shopping cart"""
    
    @staticmethod
    def get_or_create_cart(user):
        """Get user's cart or create if doesn't exist"""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    @staticmethod
    def add_to_cart(user, product_id, quantity=1):
        """Add product to cart or update quantity if exists"""
        cart = CartService.get_or_create_cart(user)
        product = get_object_or_404(Product, id=product_id)
        
        # if product already in cart, just bump up the quantity
        # TODO: add max quantity limit per item?
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item
    
    @staticmethod
    def update_item_quantity(user, product_id, quantity):
        """Update quantity of item in cart"""
        cart = CartService.get_or_create_cart(user)
        cart_item = get_object_or_404(
            CartItem,
            cart=cart,
            product_id=product_id
        )
        
        if quantity <= 0:
            cart_item.delete()
            return None
        
        cart_item.quantity = quantity
        cart_item.save()
        return cart_item
    
    @staticmethod
    def remove_from_cart(user, product_id):
        """Remove product from cart"""
        cart = CartService.get_or_create_cart(user)
        cart_item = get_object_or_404(
            CartItem,
            cart=cart,
            product_id=product_id
        )
        cart_item.delete()
        return True
    
    @staticmethod
    def clear_cart(user):
        """Clear all items from cart"""
        cart = CartService.get_or_create_cart(user)
        cart.items.all().delete()
        return True
    
    @staticmethod
    def get_cart_items(user):
        """Get all items in user's cart"""
        cart = CartService.get_or_create_cart(user)
        return cart.items.all()
    
    @staticmethod
    def get_cart_total(user):
        """Get total price of cart"""
        cart = CartService.get_or_create_cart(user)
        return cart.get_total_price()
    
    @staticmethod
    def get_cart_count(user):
        """Get total items in cart"""
        cart = CartService.get_or_create_cart(user)
        return cart.get_total_items()
