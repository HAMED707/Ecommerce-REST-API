from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Cart - {self.user.username}"
    
    def get_total_price(self):
        """Calculate total price of all items in cart"""
        # sum up all item totals
        total = sum(item.get_item_total() for item in self.items.all())
        return total
    
    def get_total_items(self):
        """Count total items in cart"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'product')  # prevents duplicate products in same cart
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def get_item_total(self):
        """Calculate total price for this item"""
        return self.product.price * self.quantity
