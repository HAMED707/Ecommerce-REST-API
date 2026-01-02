from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from payments.models import Payment, PaymentRefund
from payments.services import PaymentService
from orders.models import Order
from .serializers import (
    PaymentSerializer,
    CreatePaymentSerializer,
    ProcessPaymentSerializer,
    PaymentRefundSerializer,
    CreateRefundSerializer,
)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_list_view(request):
    """List all payments for the authenticated user."""
    # TODO: maybe add pagination here later?
    payments = Payment.objects.filter(user=request.user).select_related('order', 'user')
    serializer = PaymentSerializer(payments, many=True)
    
    return Response({
        'success': True,
        'count': payments.count(),
        'payments': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_detail_view(request, payment_id):
    """
    Get payment details by payment_id.
    GET /api/payments/{payment_id}/
    """
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    serializer = PaymentSerializer(payment)
    
    return Response({
        'success': True,
        'payment': serializer.data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment_view(request):
    """Create a new payment for an order"""
    # print(f"DEBUG: Creating payment for user {request.user.id}")  # kept for debugging
    serializer = CreatePaymentSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        order_id = serializer.validated_data['order_id']
        payment_method = serializer.validated_data['payment_method']
        payment_details = serializer.validated_data.get('payment_details', {})

        try:
            order = Order.objects.get(id=order_id, user=request.user)
            payment = PaymentService.create_payment(
                order=order,
                payment_method=payment_method,
                payment_details=payment_details
            )

            return Response(
                {
                    'success': True,
                    'message': 'Payment created successfully',
                    'payment': PaymentSerializer(payment).data
                },
                status=status.HTTP_201_CREATED
            )
        except Order.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        {'success': False, 'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_payment_view(request):
    """
    Process a payment (mock processing).
    POST /api/payments/process/
    Body: {
        "payment_id": "PAY-XXX"
    }
    """
    serializer = ProcessPaymentSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        payment_id = serializer.validated_data['payment_id']

        try:
            payment = Payment.objects.get(payment_id=payment_id, user=request.user)
            success, message = PaymentService.process_payment(payment)

            if success:
                return Response(
                    {
                        'success': True,
                        'message': message,
                        'payment': PaymentSerializer(payment).data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'success': False, 'message': message},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Payment.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    return Response(
        {'success': False, 'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_payment_view(request, payment_id):
    """Cancel a pending payment"""
    # print(f"Cancelling payment: {payment_id}")  # useful for debugging
    try:
        payment = Payment.objects.get(payment_id=payment_id, user=request.user)
        success, msg = PaymentService.cancel_payment(payment)  # shorter var name

        if success:
            return Response(
                {
                    'success': True,
                    'message': msg,
                    'payment': PaymentSerializer(payment).data
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'success': False, 'message': msg},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Payment.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Payment not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_refund_view(request):
    """Create a refund for a payment"""
    serializer = CreateRefundSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        payment_id = serializer.validated_data['payment_id']
        amount = serializer.validated_data.get('amount')  # optional
        reason = serializer.validated_data['reason']

        try:
            payment = Payment.objects.get(payment_id=payment_id, user=request.user)
            refund = PaymentService.create_refund(
                payment=payment,
                amount=amount,
                reason=reason
            )

            # Auto-process refund for mock system
            PaymentService.process_refund(refund)

            return Response(
                {
                    'success': True,
                    'message': 'Refund created and processed successfully',
                    'refund': PaymentRefundSerializer(refund).data
                },
                status=status.HTTP_201_CREATED
            )
        except Payment.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        {'success': False, 'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def refund_list_view(request):
    """
    List all refunds for the authenticated user.
    GET /api/payments/refunds/
    """
    refunds = PaymentRefund.objects.filter(
        payment__user=request.user
    ).select_related('payment', 'payment__order')
    
    serializer = PaymentRefundSerializer(refunds, many=True)
    
    return Response({
        'success': True,
        'count': refunds.count(),
        'refunds': serializer.data
    })


