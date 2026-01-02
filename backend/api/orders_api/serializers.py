from rest_framework import serializers
from orders.models import Order, OrderItem, ShippingAddress
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    item_total = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'item_total', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_product(self, obj):
        # avoid circular import
        from api.products_api.serializers import ProductSerializer
        return ProductSerializer(obj.product).data
    
    def get_item_total(self, obj):
        return obj.get_total_price()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user_email', 'status', 'payment_status',
            'shipping_address', 'shipping_city', 'shipping_postal_code',
            'shipping_country', 'phone_number', 'subtotal', 'tax',
            'shipping_cost', 'total', 'notes', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'tax', 'shipping_cost',
            'total', 'created_at', 'updated_at'
        ]


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            'id', 'full_name', 'phone_number', 'address_line1', 
            'address_line2', 'city', 'state', 'postal_code', 
            'country', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_phone_number(self, value):
        """Validate phone number format with country code"""
        if not value.strip():
            raise serializers.ValidationError("Phone number cannot be empty")
        if not value.startswith('+'):  # must have country code
            raise serializers.ValidationError(
                "Phone number must include country code (e.g., +1234567890)"
            )
        if len(value) < 10:
            raise serializers.ValidationError("Phone number is too short")
        return value
    
    def validate(self, data):
        """Additional validation - only validate address_line1 for create or when explicitly provided"""
        # TODO: simplify this validation logic
        # Check if this is a partial update (PATCH)
        is_partial = self.partial
        
        # Only validate address_line1 if:
        # 1. Not a partial update (POST or PUT)
        # 2. OR address_line1 is explicitly being updated in a PATCH
        if not is_partial:
            # For POST/PUT, address_line1 is required
            if not data.get('address_line1'):
                raise serializers.ValidationError({
                    'address_line1': 'Address line 1 is required'
                })
        else:
            # For PATCH, only validate if address_line1 is being updated
            if 'address_line1' in data and not data.get('address_line1'):
                raise serializers.ValidationError({
                    'address_line1': 'Address line 1 cannot be empty'
                })
        
        return data


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order list"""
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status',
            'total', 'item_count', 'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at']
    
    def get_item_count(self, obj):
        return obj.items.count()


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating an order from cart"""
    shipping_address = serializers.CharField(max_length=500)
    shipping_city = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=20)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    
    def validate_phone_number(self, value):
        """Validate phone number format with country code"""
        if not value:
            raise serializers.ValidationError("Phone number is required")
        if not value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number must include country code (e.g., +1234567890)"
            )
        if len(value) < 10:
            raise serializers.ValidationError("Phone number is too short")
        return value


class UpdateOrderStatusSerializer(serializers.Serializer):
    """Serializer for updating order status"""
    status = serializers.ChoiceField(
        choices=['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    )


class UpdatePaymentStatusSerializer(serializers.Serializer):
    """Serializer for updating payment status"""
    payment_status = serializers.ChoiceField(
        choices=['pending', 'completed', 'failed', 'refunded']
    )
