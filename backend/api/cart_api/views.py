from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from cart.services import CartService
from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    """Get user's cart"""
    try:
        cart = CartService.get_or_create_cart(request.user)  # creates if doesnt exist
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """Add product to cart"""
    # TODO: check stock availability before adding
    serializer = AddToCartSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data.get('quantity', 1)
        
        cart_item = CartService.add_to_cart(request.user, product_id, quantity)
        cart = CartService.get_or_create_cart(request.user)
        
        return Response(
            {
                'message': 'Product added to cart',
                'cart': CartSerializer(cart).data
            },
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, product_id):
    """Update quantity of item in cart"""
    serializer = UpdateCartItemSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        quantity = serializer.validated_data['quantity']
        cart_item = CartService.update_item_quantity(request.user, product_id, quantity)
        cart = CartService.get_or_create_cart(request.user)
        
        return Response(
            {
                'message': 'Cart updated',
                'cart': CartSerializer(cart).data
            }
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, product_id):
    """Remove product from cart"""
    try:
        CartService.remove_from_cart(request.user, product_id)
        cart = CartService.get_or_create_cart(request.user)
        
        return Response(
            {
                'message': 'Product removed from cart',
                'cart': CartSerializer(cart).data
            }
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """Clear entire cart"""
    try:
        CartService.clear_cart(request.user)
        
        return Response(
            {'message': 'Cart cleared'}
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_count(request):
    """Get total items count in cart"""
    try:
        count = CartService.get_cart_count(request.user)
        
        return Response(
            {'count': count}
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
