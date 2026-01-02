from rest_framework import serializers
from cart.models import Cart, CartItem
from products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    item_total = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_total', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_product(self, obj):
        # importing here to avoid circular import issues
        from api.products_api.serializers import ProductSerializer
        return ProductSerializer(obj.product).data
    
    def get_item_total(self, obj):
        return obj.get_item_total()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'total_items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_total_price(self, obj):
        return obj.get_total_price()
    
    def get_total_items(self, obj):
        return obj.get_total_items()


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)  # at least 1 item
    
    def validate_product_id(self, value):
        # make sure product exists before adding
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)
