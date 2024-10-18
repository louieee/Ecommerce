from django.db import models
from django.db.models import F

from core.models import BaseModel

class Unit(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Category(BaseModel):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name

class Product(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class ProductUnit(BaseModel):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    unit = models.ForeignKey("Unit", on_delete=models.SET_NULL, null=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.unit.name}(s) of {self.product.name}"


    @property
    def current_batch(self):
        return self.productbatch_set.filter(quantity__gt=0).order_by("created_at").first()

    @property
    def out_of_stock(self):
        return not self.current_batch



class ProductBatch(BaseModel):
    product_unit = models.ForeignKey("ProductUnit", on_delete=models.DO_NOTHING)
    quantity = models.PositiveIntegerField(default=0)
    cost_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    profit = models.GeneratedField(
        expression=F("selling_price") - F("cost_price"),
        output_field=models.DecimalField(decimal_places=2, max_digits=10),
        db_persist=True
    )
    total_profit = models.GeneratedField(
        expression=F("profit") * F("quantity"),
        output_field=models.DecimalField(decimal_places=2, max_digits=10),
        db_persist=True
    )

class ProductSale(BaseModel):
    product_unit = models.ForeignKey("ProductUnit", on_delete=models.DO_NOTHING)
    quantity = models.PositiveIntegerField(default=0)
    sale = models.ForeignKey("SaleTransaction", on_delete=models.CASCADE, null=True, default=None)

    def profit(self):
        return self.product_unit.current_batch.profit * self.quantity

    def total_selling_price(self):
        return self.product_unit.current_batch.selling_price * self.quantity

    def total_cost_price(self):
        return self.product_unit.current_batch.cost_price * self.quantity

class SaleTransaction(BaseModel):
    percentage_discount = models.DecimalField(default=0, max_digits=3, decimal_places=1)
    def actual_selling_price(self):
        return sum(sale.total_selling_price() for sale in self.productsale_set.all())

    def actual_profit(self):
        return self.actual_selling_price() - self.total_cost_price()

    def total_cost_price(self):
        return sum(sale.total_cost_price() for sale in self.productsale_set.all())

    def final_selling_price(self):
        return self.actual_selling_price() - (self.actual_selling_price() * (self.percentage_discount/100))

    def final_profit(self):
        return self.final_selling_price() - self.total_cost_price()