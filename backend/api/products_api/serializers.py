from rest_framework import serializers
from products.models import Product, Review


class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'user', 'user_username', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()  # count of reviews
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'image_url', 'stock', 'rating', 'average_rating', 'review_count', 'reviews', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_average_rating(self, obj):
        return obj.get_average_rating()
    
    def get_review_count(self, obj):
        return obj.get_review_count()
