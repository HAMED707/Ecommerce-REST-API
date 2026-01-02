from rest_framework import serializers
from payments.models import Payment, PaymentRefund
from orders.models import Order


class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_successful = serializers.BooleanField(read_only=True)
    can_be_refunded = serializers.BooleanField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'payment_id',
            'order',
            'order_number',
            'user',
            'user_email',
            'payment_method',
            'payment_method_display',
            'status',
            'status_display',
            'amount',
            'currency',
            'transaction_id',
            'payment_details',
            'failure_reason',
            'notes',
            'is_successful',
            'can_be_refunded',
            'created_at',
            'updated_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'payment_id',
            'user',
            'status',
            'transaction_id',
            'failure_reason',
            'created_at',
            'updated_at',
            'completed_at',
        ]


class CreatePaymentSerializer(serializers.Serializer):
    """Serializer for creating a payment for an order"""
    order_id = serializers.IntegerField(required=True)
    payment_method = serializers.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        default='card'
    )
    payment_details = serializers.JSONField(required=False, default=dict)  # optional extra data

    def validate_order_id(self, value):
        """Validate that the order exists and belongs to the user"""
        request = self.context.get('request')
        try:
            order = Order.objects.get(id=value, user=request.user)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found or does not belong to you")
        
        # make sure we dont create duplicate payments
        if hasattr(order, 'payment'):
            raise serializers.ValidationError("Payment already exists for this order")
        
        return value


class ProcessPaymentSerializer(serializers.Serializer):
    """Serializer for processing a payment"""
    payment_id = serializers.CharField(required=True)

    def validate_payment_id(self, value):
        """Validate that the payment exists and belongs to the user"""
        request = self.context.get('request')
        try:
            payment = Payment.objects.get(payment_id=value, user=request.user)
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Payment not found or does not belong to you")
        
        return value


class PaymentRefundSerializer(serializers.ModelSerializer):
    payment_id = serializers.CharField(source='payment.payment_id', read_only=True)
    order_number = serializers.CharField(source='payment.order.order_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PaymentRefund
        fields = [
            'id',
            'refund_id',
            'payment',
            'payment_id',
            'order_number',
            'amount',
            'status',
            'status_display',
            'reason',
            'refund_transaction_id',
            'created_at',
            'updated_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'refund_id',
            'status',
            'refund_transaction_id',
            'created_at',
            'updated_at',
            'completed_at',
        ]


class CreateRefundSerializer(serializers.Serializer):
    """
    Serializer for creating a refund.
    """
    payment_id = serializers.CharField(required=True)
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    reason = serializers.CharField(required=True, max_length=1000)

    def validate_payment_id(self, value):
        """Validate that the payment exists and can be refunded"""
        request = self.context.get('request')
        try:
            payment = Payment.objects.get(payment_id=value, user=request.user)
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Payment not found or does not belong to you")
        
        if not payment.can_be_refunded:
            raise serializers.ValidationError("Payment cannot be refunded")
        
        return value

    def validate_amount(self, value):
        """Validate refund amount"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Refund amount must be greater than 0")
        return value
