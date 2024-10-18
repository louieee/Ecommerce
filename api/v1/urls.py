from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import SimpleRouter

from api.v1.views import UnitAPI, CategoryAPI, ProductBatchAPI, SaleAPI, ProductAPI, ProductListAPI, ProductUnitListAPI

swagger_view = get_schema_view(
    info=openapi.Info(
        title=f"Ecommerce Backend API",
        default_version="Version 1",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = SimpleRouter()
router.register("units", UnitAPI, basename="unit")
router.register("categories", CategoryAPI, basename="categories")
router.register("product-batches", ProductBatchAPI, basename="product-batches")
router.register("sales", SaleAPI, basename="sales")
router.register("products", ProductAPI, basename="products")

urlpatterns = [
    path("docs/", swagger_view.with_ui("swagger", cache_timeout=0), name="swagger_docs"
    ),
    path(
        "re-docs/",
        swagger_view.with_ui("redoc", cache_timeout=0),
        name="swagger_redocs",
    ),
    path("products", ProductListAPI.as_view()),
    path("product-units", ProductUnitListAPI.as_view())
]
urlpatterns += router.urls
