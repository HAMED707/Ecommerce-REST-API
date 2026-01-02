from django.utils import timezone
from django.db import transaction
from .models import Payment, PaymentRefund
from orders.models import Order


class PaymentService:
    """Service class for handling payment operations (mock implementation)"""

    @staticmethod
    def create_payment(order, payment_method='card', payment_details=None):
        """Create a new payment for an order"""
        # check if payment already exists
        if hasattr(order, 'payment'):
            raise ValueError(f"Payment already exists for order {order.order_number}")
        
        payment = Payment.objects.create(
            order=order,
            user=order.user,
            payment_method=payment_method,
            amount=order.total,
            status='pending',
            payment_details=payment_details or {}
        )
        
        return payment

    @staticmethod
    @transaction.atomic
    def process_payment(payment):
        """Process a payment (mock - in real app use Stripe/PayPal)"""
        # TODO: integrate real payment gateway
        if payment.status == 'completed':
            return False, "Payment already completed"
        
        # Mock payment processing logic
        if payment.payment_method == 'cod':
            # Cash on Delivery - mark as pending until delivery
            payment.status = 'pending'
            payment.transaction_id = f"COD-{payment.payment_id}"
            payment.save()
            
            # Update order
            payment.order.payment_status = 'pending'
            payment.order.status = 'processing'
            payment.order.save()
            
            # Clear cart after COD order confirmed
            PaymentService._clear_cart_after_payment(payment.user)
            
            return True, "Cash on Delivery order created successfully"
        
        elif payment.payment_method == 'demo':
            # Demo payment - auto complete
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.transaction_id = f"DEMO-{payment.payment_id}"
            payment.save()
            
            # Update order payment status
            payment.order.payment_status = 'completed'
            payment.order.status = 'processing'
            payment.order.save()
            
            # Clear cart after successful payment
            PaymentService._clear_cart_after_payment(payment.user)
            
            return True, "Demo payment completed successfully"
        
        else:
            # Card, bank_transfer, wallet - simulate processing
            payment.status = 'processing'
            payment.transaction_id = f"TXN-{payment.payment_id}"
            payment.save()
            
            # In real scenario, you would:
            # 1. Call payment gateway API (Stripe/PayPal)
            # 2. Wait for response or webhook
            # 3. Update status based on gateway response
            # print("Would call payment gateway here...")  # debug
            
            # For mock, we auto-complete it
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update order payment status
            payment.order.payment_status = 'completed'
            payment.order.status = 'processing'
            payment.order.save()
            
            # Clear cart after successful payment
            PaymentService._clear_cart_after_payment(payment.user)
            
            return True, f"Payment processed successfully via {payment.get_payment_method_display()}"

    @staticmethod
    def _clear_cart_after_payment(user):
        """Clear user's cart after successful payment"""
        from cart.models import Cart, CartItem
        
        try:
            cart = Cart.objects.get(user=user)
            # Delete all cart items
            CartItem.objects.filter(cart=cart).delete()
        except Cart.DoesNotExist:
            pass  # no cart, nothing to clear

    @staticmethod
    def mark_payment_completed(payment, transaction_id=None):
        """Mark a payment as completed (for manual completion or webhook)"""
        if payment.status == 'completed':
            return False, "Payment already completed"
        
        payment.status = 'completed'
        payment.completed_at = timezone.now()
        
        if transaction_id:
            payment.transaction_id = transaction_id
        
        payment.save()
        
        # Update order payment status
        payment.order.payment_status = 'completed'
        payment.order.save()
        
        return True, "Payment marked as completed"

    @staticmethod
    def mark_payment_failed(payment, reason=None):
        """Mark a payment as failed"""
        payment.status = 'failed'  # update status
        payment.failure_reason = reason or "Payment processing failed"
        payment.save()
        
        # also update order
        payment.order.payment_status = 'failed'
        payment.order.save()
        
        return True, "Payment marked as failed"

    @staticmethod
    def cancel_payment(payment):
        """Cancel a pending payment"""
        # cant cancel if already completed
        if payment.status == 'completed':
            return False, "Cannot cancel completed payment. Use refund instead."
        
        payment.status = 'cancelled'
        payment.save()
        
        # Update order payment status
        payment.order.payment_status = 'cancelled'
        payment.order.save()
        
        return True, "Payment cancelled successfully"

    @staticmethod
    @transaction.atomic
    def create_refund(payment, amount=None, reason=""):
        """Create a refund for a completed payment"""
        # TODO: add partial refund support
        if payment.status != 'completed':
            raise ValueError("Can only refund completed payments")
        
        if hasattr(payment, 'refund'):
            raise ValueError("Refund already exists for this payment")
        
        refund_amount = amount or payment.amount  # default to full amount
        
        if refund_amount > payment.amount:
            raise ValueError("Refund amount cannot exceed payment amount")
        
        refund = PaymentRefund.objects.create(
            payment=payment,
            amount=refund_amount,
            reason=reason,
            status='pending'
        )
        
        return refund

    @staticmethod
    @transaction.atomic
    def process_refund(refund):
        """Process a refund (mock - would call payment gateway API)"""
        if refund.status == 'completed':
            return False, "Refund already completed"
        
        # Mock refund processing
        refund.status = 'processing'
        refund.save()
        
        # In real scenario, call payment gateway refund API here
        
        # Auto-complete for mock
        refund.status = 'completed'
        refund.completed_at = timezone.now()
        refund.refund_transaction_id = f"REFUND-{refund.refund_id}"
        refund.save()
        
        # Update payment status
        refund.payment.status = 'refunded'
        refund.payment.save()
        
        # Update order payment status
        refund.payment.order.payment_status = 'refunded'
        refund.payment.order.status = 'cancelled'
        refund.payment.order.save()
        
        # Restore product stock after refund
        PaymentService._restore_stock_after_refund(refund.payment.order)
        
        return True, "Refund processed successfully"

    @staticmethod
    def _restore_stock_after_refund(order):
        """Restore product stock after refund"""
        from orders.models import OrderItem
        
        order_items = OrderItem.objects.filter(order=order)
        
        for item in order_items:
            # add quantity back to stock
            item.product.stock += item.quantity
            item.product.save()

    @staticmethod
    def get_payment_by_order(order):
        """Get payment for an order"""
        try:
            return Payment.objects.get(order=order)
        except Payment.DoesNotExist:
            return None
