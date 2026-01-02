from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.services import OrderService, ShippingAddressService
from orders.models import ShippingAddress
from .serializers import (
    OrderSerializer, 
    OrderListSerializer,
    CreateOrderSerializer,
    UpdateOrderStatusSerializer,
    ShippingAddressSerializer
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create a new order from user's cart"""
    # NOTE: make sure cart is not empty before calling this!
    serializer = CreateOrderSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            order = OrderService.create_order_from_cart(
                user=request.user,
                shipping_data=serializer.validated_data
            )
            order_serializer = OrderSerializer(order)
            return Response(
                {
                    'message': 'Order created successfully',
                    'order': order_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to create order'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request):
    """
    Get all orders for authenticated user
    GET /api/orders/
    """
    orders = OrderService.get_user_orders(request.user)
    serializer = OrderListSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """
    Get specific order details
    GET /api/orders/<order_id>/
    """
    try:
        order = OrderService.get_order_by_id(request.user, order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_by_number(request, order_number):
    """
    Get order by order number
    GET /api/orders/number/<order_number>/
    """
    try:
        order = OrderService.get_order_by_number(request.user, order_number)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    """Cancel an order"""
    # TODO: add confirmation email
    try:
        order = OrderService.cancel_order(request.user, order_id)
        serializer = OrderSerializer(order)
        return Response(
            {
                'message': 'Order cancelled successfully',
                'order': serializer.data
            }
        )
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to cancel order'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Update order status (admin only in production)"""
    serializer = UpdateOrderStatusSerializer(data=request.data)
    
    # validate first
    if serializer.is_valid():
        try:
            order = OrderService.update_order_status(
                order_id=order_id,
                status=serializer.validated_data['status']
            )
            order_serializer = OrderSerializer(order)
            return Response(order_serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ==================== SHIPPING ADDRESS VIEWS ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def shipping_address_list(request):
    """Get all shipping addresses or create new one"""
    if request.method == 'GET':
        addresses = ShippingAddressService.get_user_addresses(request.user)
        serializer = ShippingAddressSerializer(addresses, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ShippingAddressSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            address = ShippingAddressService.create_address(
                user=request.user,
                address_data=serializer.validated_data
            )
            
            return Response(
                {
                    'message': 'Shipping address created successfully',
                    'address': ShippingAddressSerializer(address).data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def shipping_address_detail(request, address_id):
    """
    Get, update or delete a shipping address
    GET /api/orders/shipping-addresses/<address_id>/
    PUT/PATCH /api/orders/shipping-addresses/<address_id>/
    DELETE /api/orders/shipping-addresses/<address_id>/
    """
    try:
        address = ShippingAddress.objects.get(
            id=address_id,
            user=request.user
        )
    except ShippingAddress.DoesNotExist:
        return Response(
            {'error': 'Shipping address not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = ShippingAddressSerializer(address)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = ShippingAddressSerializer(
            data=request.data,
            partial=partial
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            updated_address = ShippingAddressService.update_address(
                address=address,
                address_data=serializer.validated_data
            )
            
            return Response({
                'message': 'Shipping address updated successfully',
                'address': ShippingAddressSerializer(updated_address).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    elif request.method == 'DELETE':
        try:
            ShippingAddressService.delete_address(address)
            return Response(
                {'message': 'Shipping address deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_default_address(request, address_id):
    """
    Set a shipping address as default
    POST /api/orders/shipping-addresses/<address_id>/set-default/
    """
    try:
        address = ShippingAddressService.set_default_address(
            user=request.user,
            address_id=address_id
        )
        
        return Response({
            'message': 'Default address set successfully',
            'address': ShippingAddressSerializer(address).data
        })
    except ShippingAddress.DoesNotExist:
        return Response(
            {'error': 'Shipping address not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_default_address(request):
    """
    Get user's default shipping address
    GET /api/orders/shipping-addresses/default/
    """
    address = ShippingAddressService.get_default_address(request.user)
    
    if not address:
        return Response(
            {'message': 'No default address set'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ShippingAddressSerializer(address)
    return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
