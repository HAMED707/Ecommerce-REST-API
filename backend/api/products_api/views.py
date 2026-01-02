from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from products.services import ProductService
from products.models import Review
from .serializers import ProductSerializer, ReviewSerializer


@api_view(['GET'])
def product_list(request):
    """Get all products or search/filter"""
    # TODO: refactor this - too many if statements
    search = request.query_params.get('search', None)
    if search:
        products = ProductService.search_products(search)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    # Filter by category
    category = request.query_params.get('category', None)
    if category:
        products = ProductService.filter_by_category(category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    # Filter by price
    min_price = request.query_params.get('min_price', None)
    max_price = request.query_params.get('max_price', None)
    if min_price and max_price:
        products = ProductService.filter_by_price(float(min_price), float(max_price))
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    # Get all products
    products = ProductService.get_all_products()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def product_detail(request, product_id):
    """Get single product"""
    product = ProductService.get_product_by_id(product_id)
    
    if not product:
        return Response(
            {'error': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view(['GET'])
def featured_products(request):
    """Get featured products"""
    products = ProductService.get_featured_products()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, product_id):
    """Add review to product"""
    try:
        product = ProductService.get_product_by_id(product_id)
        # quick check if product exists
        if not product:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ReviewSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save review with user and product
        serializer.save(user=request.user, product=product)
        
        return Response(
            {
                'message': 'Review added successfully',
                'review': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def product_reviews(request, product_id):
    """Get all reviews for a product"""
    try:
        product = ProductService.get_product_by_id(product_id)
        
        if not product:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        reviews = product.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        
        return Response({
            'product': product.name,
            'average_rating': product.get_average_rating(),
            'review_count': product.get_review_count(),
            'reviews': serializer.data
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
