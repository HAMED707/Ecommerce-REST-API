from django.db import models
from django.conf import settings
from orders.models import Order
import uuid


class Payment(models.Model):
    """Payment model for tracking order payments"""
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('wallet', 'Digital Wallet'),
        ('demo', 'Demo Payment'),  # for testing
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    # Basic fields
    payment_id = models.CharField(max_length=100, unique=True, editable=False)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    # Payment details
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='card'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Additional information
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional payment information (last 4 digits, bank name, etc.)"
    )
    failure_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['status']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Payment {self.payment_id} - {self.get_payment_method_display()} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.payment_id:
            # Generate unique payment ID
            self.payment_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        
        # auto-set user from order if missing
        if not self.user_id and self.order:
            self.user = self.order.user
        
        # Set amount from order total if not set
        if not self.amount and self.order:
            self.amount = self.order.total
            
        super().save(*args, **kwargs)

    @property
    def is_successful(self):
        """Check if payment was successful"""
        return self.status == 'completed'

    @property
    def can_be_refunded(self):
        """Check if payment can be refunded"""
        return self.status == 'completed' and not hasattr(self, 'refund')


class PaymentRefund(models.Model):
    """
    Model for tracking refunds of payments.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    refund_id = models.CharField(max_length=100, unique=True, editable=False)
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='refund'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    reason = models.TextField()
    refund_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund {self.refund_id} for Payment {self.payment.payment_id}"

    def save(self, *args, **kwargs):
        if not self.refund_id:
            self.refund_id = f"REF-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
