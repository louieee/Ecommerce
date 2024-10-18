from datetime import timedelta
from decimal import Decimal

from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from app.models import Unit, Category, Product, ProductUnit, ProductBatch, ProductSale, SaleTransaction


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ("id", "name")


    def validate_name(self, value):
        return str(value).lower()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")

    # def validate_name(self, value):
    #     return str(value).lower()
    def validate_name(self, value):
        return str(value).lower()


class MutateProductSerializer(serializers.ModelSerializer):
    units = serializers.PrimaryKeyRelatedField(many=True, queryset=Unit.objects.all())
    class Meta:
        model = Product
        fields = ("name",  "category", "units", )

    def validate_name(self, value):
        return str(value).lower()

    def create(self, validated_data):
        units = validated_data.pop('units')
        product = Product.objects.create(**validated_data)
        for unit in units:
            ProductUnit.objects.get_or_create(product=product, unit=unit)
        return product

    def update(self, instance, validated_data):
        units = validated_data.pop('units')
        instance = super().update(instance, validated_data)
        ProductUnit.objects.filter(Q(product=instance) & ~Q(unit__in=units)).update(archived=True)
        for unit in units:
            ProductUnit.objects.get_or_create(product=instance, unit=unit)
        return instance

class ProductBatchSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product_unit.product.name")
    unit = serializers.CharField(source="product_unit.unit.name")
    class Meta:
        model = ProductBatch
        exclude = ("deleted_at", "restored_at", )

class ProductBatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBatch
        exclude = ("deleted_at", "restored_at", )

class MutateProductBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBatch
        exclude = ("deleted_at", "restored_at", "transaction" )

class ProductUnitSerializer(serializers.ModelSerializer):
    unit = serializers.CharField(source="unit.name")
    product = serializers.CharField(source="product.name")
    out_of_stock = serializers.BooleanField(read_only=True)
    selling_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2,
                                             source="current_batch.selling_price")
    cost_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2,
                                             source="current_batch.cost_price")
    quantity_left = serializers.IntegerField(read_only=True, source="current_batch.quantity")


    class Meta:
        model = ProductUnit
        exclude = ("deleted_at", "restored_at", )

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ("deleted_at", "restored_at", )

class CreateProductBatchSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1)


    class Meta:
        model = ProductBatch
        fields = ("product_unit", "quantity", "cost_price", "selling_price")


    def validate(self, attrs):
        if attrs["selling_price"] < attrs["cost_price"]:
            raise serializers.ValidationError("Selling price cannot be less than cost price")
        if not self.instance:
            last_2_minutes = timezone.now() - timedelta(minutes=2)
            if ProductBatch.objects.filter(**attrs, created_at__range=(last_2_minutes, timezone.now())).exists():
                raise serializers.ValidationError("Try again in 2 minutes")
        return attrs

    def create(self, validated_data):
        return ProductBatch.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance = instance.update(**validated_data)
        return instance

class UpdateProductBatchSerializer(CreateProductBatchSerializer):
    unit = None
    product = None
    quantity = None

    class Meta:
        model = ProductBatch
        fields = ("cost_price", "selling_price")



class CreateSaleItemSerializer(serializers.ModelSerializer):
    product_unit = serializers.PrimaryKeyRelatedField(queryset=ProductUnit.objects.all())
    quantity = serializers.IntegerField()
    class Meta:
        model = ProductSale
        fields = ("product_unit", "quantity", )

    def validate(self, attrs):
        product_unit = attrs["product_unit"]
        if product_unit.out_of_stock:
            raise serializers.ValidationError(f"{product_unit} is out of stock")
        product_quantity = product_unit.current_batch.quantity
        if product_quantity < attrs["quantity"]:
            raise serializers.ValidationError(f"Only {product_quantity} {product_unit} is available")
        attrs["cost_price"] = product_unit.current_batch.cost_price
        attrs["selling_price"] = product_unit.current_batch.selling_price
        return attrs






class SaleItemSerializer(serializers.ModelSerializer):
    product_unit = serializers.CharField(read_only=True)
    profit = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    total_selling_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    total_cost_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    class Meta:
        model = ProductSale
        exclude = ("deleted_at", "restored_at", )



class CreateSaleTransactionSerializer(serializers.ModelSerializer):
    sales = CreateSaleItemSerializer(many=True)
    percentage_discount = serializers.DecimalField(max_value=Decimal(100), min_value=Decimal(0), decimal_places=1, max_digits=3, required=False)
    class Meta:
        model = SaleTransaction
        fields = ("sales", "percentage_discount", )

    def create(self, validated_data):
        sales = validated_data.pop("sales")
        transaction = SaleTransaction.objects.create(**validated_data)
        for sale in sales:
            ProductSale.objects.create(**sale, sale=transaction)
        return transaction

class SaleTransactionSerializer(serializers.ModelSerializer):
    sales = SaleItemSerializer(many=True, source="productsale_set", read_only=True)
    actual_selling_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    actual_profit = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    total_cost_price = serializers.DecimalField( read_only=True, max_digits=10, decimal_places=2)
    final_profit = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    final_selling_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    class Meta:
        model = SaleTransaction
        exclude = ("deleted_at", "restored_at", )