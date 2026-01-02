from django.db import transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import Order, OrderItem, ShippingAddress
from cart.models import Cart, CartItem
from products.models import Product

class ShippingAddressService:
    """Business logic for shipping address management"""
    
    @staticmethod
    def create_address(user, address_data):
        """Create a new shipping address for user"""
        with transaction.atomic():
            # If this is set as default, unset other defaults
            if address_data.get('is_default', False):
                ShippingAddress.objects.filter(
                    user=user, 
                    is_default=True
                ).update(is_default=False)
            
            address = ShippingAddress.objects.create(
                user=user,
                **address_data
            )
            return address
    
    @staticmethod
    def update_address(address, address_data):
        """Update existing shipping address"""
        with transaction.atomic():
            # If setting as default, unset other defaults
            if address_data.get('is_default', False):
                ShippingAddress.objects.filter(
                    user=address.user,
                    is_default=True
                ).exclude(pk=address.pk).update(is_default=False)
            
            for key, value in address_data.items():
                setattr(address, key, value)
            address.save()
            return address
    
    @staticmethod
    def set_default_address(user, address_id):
        """Set a specific address as default"""
        with transaction.atomic():
            # Unset all defaults
            ShippingAddress.objects.filter(
                user=user,
                is_default=True
            ).update(is_default=False)
            
            # Set the new default
            address = ShippingAddress.objects.get(
                id=address_id,
                user=user
            )
            address.is_default = True
            address.save()
            return address
    
    @staticmethod
    def get_user_addresses(user):
        """Get all addresses for a user"""
        return ShippingAddress.objects.filter(user=user)
    
    @staticmethod
    def get_default_address(user):
        """Get user's default address"""
        try:
            return ShippingAddress.objects.get(
                user=user,
                is_default=True
            )
        except ShippingAddress.DoesNotExist:
            return None
    
    @staticmethod
    def delete_address(address):
        """Delete a shipping address"""
        address.delete()

class OrderService:
    """Business logic for order management"""
    
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, shipping_data):
        """Create an order from user's cart"""
        # Get user's cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise ValueError("Cart is empty")
        
        cart_items = cart.items.all()
        if not cart_items.exists():
            raise ValueError("Cart is empty")  # shouldn't happen but just in case
        
        # Validate stock availability
        for item in cart_items:
            if item.product.stock < item.quantity:
                raise ValueError(f"Insufficient stock for {item.product.name}")
        
        # Calculate totals
        subtotal = cart.get_total_price()
        tax = OrderService._calculate_tax(subtotal)  # TODO: make tax rates configurable
        shipping_cost = OrderService._calculate_shipping(subtotal)
        total = subtotal + tax + shipping_cost
        
        # Create order
        order = Order.objects.create(
            user=user,
            status='pending',
            payment_status='pending',
            shipping_address=shipping_data['shipping_address'],
            shipping_city=shipping_data['shipping_city'],
            shipping_postal_code=shipping_data['shipping_postal_code'],
            shipping_country=shipping_data['shipping_country'],
            phone_number=shipping_data['phone_number'],
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            total=total,
            notes=shipping_data.get('notes', '')
        )
        
        # Create order items and update stock
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            # Reduce product stock
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()
        
        # Clear cart
        cart_items.delete()
        
        return order
    
    @staticmethod
    def _calculate_tax(subtotal):
        """Calculate tax (10% for demo)"""
        # TODO: make tax rate configurable per region
        tax_rate = Decimal('0.10')
        return (subtotal * tax_rate).quantize(Decimal('0.01'))
    
    @staticmethod
    def _calculate_shipping(subtotal):
        """Calculate shipping cost"""
        if subtotal >= 100:
            return Decimal('0.00')  # free shipping for orders over $100
        return Decimal('10.00')  # flat rate otherwise
    
    @staticmethod
    def get_user_orders(user):
        """Get all orders for a user"""
        return Order.objects.filter(user=user).prefetch_related('items__product')
    
    @staticmethod
    def get_order_by_id(user, order_id):
        """Get specific order for a user"""
        return get_object_or_404(Order, id=order_id, user=user)
    
    @staticmethod
    def get_order_by_number(user, order_number):
        """Get order by order number"""
        return get_object_or_404(Order, order_number=order_number, user=user)
    
    @staticmethod
    @transaction.atomic
    def cancel_order(user, order_id):
        """Cancel an order and restore stock"""
        order = OrderService.get_order_by_id(user, order_id)
        
        # cant cancel if already shipped/delivered
        if order.status not in ['pending', 'processing']:
            raise ValueError("Cannot cancel order that has been shipped or delivered")
        
        # Restore product stock
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()
        
        # Update order status
        order.status = 'cancelled'
        order.payment_status = 'refunded'
        order.save()
        
        return order
    
    @staticmethod
    def update_order_status(order_id, status):
        """Update order status (admin function)"""
        order = get_object_or_404(Order, id=order_id)
        
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        order.status = status
        order.save()
        return order
    
    @staticmethod
    def update_payment_status(order_id, payment_status):
        """Update payment status (admin/payment gateway function)"""
        order = get_object_or_404(Order, id=order_id)
        
        valid_statuses = ['pending', 'completed', 'failed', 'refunded']
        if payment_status not in valid_statuses:
            raise ValueError(f"Invalid payment status. Must be one of: {', '.join(valid_statuses)}")
        
        order.payment_status = payment_status
        order.save()
        return order
