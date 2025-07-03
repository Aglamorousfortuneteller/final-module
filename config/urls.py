from django.contrib import admin
from django.urls import path
from crm.views import RegisterView, CompanyCreateView, CompanyDetailView, StorageCreateView, StorageDetailView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/company/', CompanyCreateView.as_view(), name='create_company'),
    path('api/company/detail/', CompanyDetailView.as_view(), name='company_detail'),
    path('api/storage/', StorageCreateView.as_view(), name='create_storage'),
    path('api/storage/detail/', StorageDetailView.as_view(), name='storage_detail'),

]
