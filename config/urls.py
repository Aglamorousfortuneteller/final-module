from django.urls import path, re_path
from django.views.generic import RedirectView
from crm.views import (
    RegisterView,
    CompanyCreateView,
    CompanyDetailView,
    StorageCreateView,
    StorageDetailView,
    SupplierListCreateView,
    SupplierRetrieveUpdateDestroyView,
    ProductListCreateView,
    ProductRetrieveUpdateDestroyView,
    SupplyListCreateView,
    AttachUserToCompanyView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.contrib import admin


schema_view = get_schema_view(
    openapi.Info(
        title="Final Module API",
        default_version='v1',
        description="API documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),

    path('admin/', admin.site.urls),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/register/', RegisterView.as_view(), name='register'),

    path('api/company/', CompanyCreateView.as_view(), name='create_company'),
    path('api/company/detail/', CompanyDetailView.as_view(), name='company_detail'),

    path('api/storage/', StorageCreateView.as_view(), name='create_storage'),
    path('api/storage/detail/', StorageDetailView.as_view(), name='storage_detail'),

    # Suppliers
    path('api/suppliers/', SupplierListCreateView.as_view(), name='supplier_list_create'),
    path('api/suppliers/<int:pk>/', SupplierRetrieveUpdateDestroyView.as_view(), name='supplier_detail'),

    # Products
    path('api/products/', ProductListCreateView.as_view(), name='product_list_create'),
    path('api/products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product_detail'),

    # Supplies
    path('api/supplies/', SupplyListCreateView.as_view(), name='supply_list_create'),

    # Attach user to company (only for company owner)
    path('api/company/attach-user/', AttachUserToCompanyView.as_view(), name='attach_user_to_company'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
