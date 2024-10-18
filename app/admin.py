from django.contrib import admin

# Register your models here.

from app.models import Product, SaleTransaction, ProductUnit, ProductBatch, Category, Unit, ProductSale

admin.site.register(Product)
admin.site.register(SaleTransaction)
admin.site.register(ProductUnit)
admin.site.register(ProductBatch)
admin.site.register(Category)
admin.site.register(Unit)
admin.site.register(ProductSale)
