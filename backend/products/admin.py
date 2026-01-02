from django.contrib import admin
from .models import Product, Review

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'stock', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')  # allows searching
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'rating', 'user', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'comment')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'price', 'category')
        }),
        ('Media', {
            'fields': ('image_url',)
        }),
        ('Inventory', {
            'fields': ('stock',)
        }),
        ('Rating & Status', {
            'fields': ('rating', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
