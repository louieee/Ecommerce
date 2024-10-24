import logging

from django.db import transaction
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.serializers import UnitSerializer, CategorySerializer, ProductBatchSerializer, SaleTransactionSerializer, \
    CreateSaleTransactionSerializer, CreateProductBatchSerializer, UpdateProductBatchSerializer, ProductSerializer, \
    MutateProductSerializer, ProductUnitSerializer
from app.models import Unit, Category, ProductBatch, SaleTransaction, Product, ProductUnit

search_query  = openapi.Parameter(
    name="search",
    in_=openapi.IN_QUERY,
    description="Search query",
    type=openapi.TYPE_STRING
)

product_query = openapi.Parameter(
    name="product",
    in_=openapi.IN_QUERY,
    description="Product id",
    type=openapi.TYPE_NUMBER
)

unit_query = openapi.Parameter(
    name="unit",
    in_=openapi.IN_QUERY,
    description="Unit id",
    type=openapi.TYPE_NUMBER
)

class UnitAPI(viewsets.ModelViewSet):
    queryset = Unit.objects.order_by("name")
    serializer_class = UnitSerializer
    http_method_names = ("get", "post", "patch",)

    def filter_queryset(self, queryset):
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    @swagger_auto_schema(
        operation_summary="update unit"
    )
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="create unit"
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="list units",
        manual_parameters=[search_query]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="retrieve unit",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class CategoryAPI(viewsets.ModelViewSet):
    queryset = Category.objects.order_by("name")
    serializer_class = CategorySerializer
    http_method_names = ("get", "post", "patch",)

    def filter_queryset(self, queryset):
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    @swagger_auto_schema(
        operation_summary="update product category"
    )
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="create product category"
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="list product categories",
        manual_parameters=[search_query]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="retrieve product category",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class ProductBatchAPI(viewsets.ModelViewSet):
    queryset = ProductBatch.objects.order_by("-id")
    serializer_class = ProductBatchSerializer
    # permission_classes = (IsAuthenticated,)
    http_method_names = ("post", "patch", "get")

    def filter_queryset(self, queryset):
        product = self.request.query_params.get("product")
        unit = self.request.query_params.get("unit")
        if product:
            queryset = queryset.filter(product_unit__product_id=product)
        if unit:
            queryset = queryset.filter(product_unit__unit_id=unit)
        return queryset

    @swagger_auto_schema(
        request_body=CreateProductBatchSerializer,
        operation_summary="create product batch"
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = CreateProductBatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=400)
        batch = serializer.save()
        return Response(data=self.serializer_class(batch).data, status=201)

    @swagger_auto_schema(
        request_body=UpdateProductBatchSerializer,
        operation_summary="update product batch"
    )
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        serializer = UpdateProductBatchSerializer(data=request.data, partial=True,
                                                  instance=self.get_object())
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=400)
        batch = serializer.save()
        return Response(data=self.serializer_class(batch).data, status=200)

    @swagger_auto_schema(
        operation_summary="list product batches",
        manual_parameters=[product_query, unit_query]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="retrieve product batch",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class SaleAPI(viewsets.ModelViewSet):
    queryset = SaleTransaction.objects.order_by("-id")
    serializer_class = SaleTransactionSerializer
    http_method_names = ("post", "get")

    @swagger_auto_schema(
        request_body=CreateSaleTransactionSerializer,
        operation_summary="create sale transaction"
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = CreateSaleTransactionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=400)
        sale = serializer.save()
        return Response(data=self.serializer_class(sale).data, status=201)

    @swagger_auto_schema(
        operation_summary="list sale transactions"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="list sale transactions"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductAPI(viewsets.ModelViewSet):
    queryset = Product.objects.order_by("name")
    serializer_class = ProductSerializer
    http_method_names = ("post", "patch")

    def filter_queryset(self, queryset):
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(category__name__icontains=search)|
                Q(productunit__unit__name__icontains=search))

        return queryset

    @swagger_auto_schema(
        request_body=MutateProductSerializer,
        operation_summary="create product",
        tags=["products"]
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = MutateProductSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response(data=serializer.errors, status=400)
        product = serializer.save()
        return Response(data=self.serializer_class(product).data, status=201)

    @swagger_auto_schema(
        request_body=MutateProductSerializer,
        operation_summary="update product",
        tags=["products"]
    )
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        serializer = MutateProductSerializer(data=request.data, partial=True,
                                             instance=self.get_object())
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=400)
        product = serializer.save()
        return Response(data=self.serializer_class(product).data, status=200)

    @swagger_auto_schema(
        operation_summary="retrieve product"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="list products",
        manual_parameters=[search_query]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ProductUnitListAPI(ListAPIView):
    queryset = ProductUnit.objects.order_by("product_id")
    serializer_class = ProductUnitSerializer
    http_method_names = ("get",)

    def filter_queryset(self, queryset):
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(unit__name__icontains=search)
                                       |Q(product__name__icontains=search))
        return queryset

    @swagger_auto_schema(
        operation_summary="list product units",
        manual_parameters=[search_query],
        tags=["products"]

    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductListAPI(ListAPIView):
    queryset = Product.objects.order_by("name")
    serializer_class = ProductSerializer
    http_method_names = ("get",)

    def filter_queryset(self, queryset):
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    @swagger_auto_schema(
        operation_summary="list of products",
        manual_parameters=[search_query],
        tags=["products"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)