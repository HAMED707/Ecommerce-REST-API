from django.contrib import admin
from .models import Payment, PaymentRefund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_id',
        'order',
        'user',
        'payment_method',
        'amount',
        'status',
        'created_at',
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['payment_id', 'order__order_number', 'user__email', 'transaction_id']
    readonly_fields = ['payment_id', 'created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'order', 'user', 'amount', 'currency')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'status', 'transaction_id', 'payment_details')
        }),
        ('Additional Information', {
            'fields': ('failure_reason', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of completed payments
        # TODO: maybe add a soft delete instead?
        if obj and obj.status == 'completed':
            return False  # cant delete completed payments
        return super().has_delete_permission(request, obj)


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = [
        'refund_id',
        'payment',
        'amount',
        'status',
        'created_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['refund_id', 'payment__payment_id', 'refund_transaction_id']
    readonly_fields = ['refund_id', 'created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Refund Information', {
            'fields': ('refund_id', 'payment', 'amount', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'refund_transaction_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
