from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'city', 'country', 'is_default', 'created_at']
    list_filter = ['is_default', 'country', 'created_at']
    search_fields = ['full_name', 'user__email', 'city', 'address_line1']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'full_name', 'phone_number')
        }),
        ('Address Details', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 
                      'postal_code', 'country', 'is_default')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # no extra blank rows
    readonly_fields = ('product', 'quantity', 'price', 'get_total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__email', 'shipping_address']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'notes')
        }),
        ('Shipping Details', {
            'fields': ('saved_shipping_address', 'shipping_address', 'shipping_city', 
                      'shipping_postal_code', 'shipping_country', 'phone_number')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax', 'shipping_cost', 'total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'get_total_price']
    list_filter = ['order__status', 'created_at']
    search_fields = ['order__order_number', 'product__name']
