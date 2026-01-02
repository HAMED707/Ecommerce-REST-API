from django.core.management.base import BaseCommand
from products.models import Product
import requests


class Command(BaseCommand):
    help = 'Populate database with products from Fake Store API'

    def handle(self, *args, **options):
        try:
            # Fetch products from Fake Store API
            response = requests.get('https://fakestoreapi.com/products')
            response.raise_for_status()
            products_data = response.json()
            
            for product_data in products_data:
                # Map category names to our choices
                category_mapping = {
                    'electronics': 'clothing',  # Map to our available categories
                    'jewelery': 'accessories',
                    'men\'s clothing': 'clothing',
                    'women\'s clothing': 'clothing',
                }
                
                category = category_mapping.get(
                    product_data['category'].lower(),
                    'clothing'
                )
                
                product, created = Product.objects.get_or_create(
                    id=product_data['id'],
                    defaults={
                        'name': product_data['title'],
                        'description': product_data['description'],
                        'price': product_data['price'],
                        'category': category,
                        'image_url': product_data['image'],
                        'rating': product_data['rating']['rate'],
                        'stock': 100,
                        'is_active': True,
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created: {product.name[:50]}...')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Already exists: {product.name[:50]}...')
                    )

            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Successfully populated {len(products_data)} products from Fake Store API!')
            )
            
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error fetching from API: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error: {str(e)}')
            )

