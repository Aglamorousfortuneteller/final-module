from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Company, Storage, Supplier, Product, Supply, SupplyProduct
from .serializers import (
    RegisterSerializer,
    CompanySerializer,
    StorageSerializer,
    SupplierSerializer,
    ProductSerializer,
    SupplySerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CompanyCreateView(generics.CreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_company_owner and user.company is not None:
            raise ValidationError("Пользователь уже является владельцем компании.")
        company = serializer.save()
        user.company = company
        user.is_company_owner = True
        user.save()


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if user.company is None:
            raise ValidationError("Пользователь не привязан к компании.")
        return user.company

    def perform_update(self, serializer):
        if not self.request.user.is_company_owner:
            raise ValidationError("Только владелец компании может редактировать данные.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_company_owner:
            raise ValidationError("Только владелец компании может удалить компанию.")
        user.company = None
        user.is_company_owner = False
        user.save()
        instance.delete()


class StorageCreateView(generics.CreateAPIView):
    serializer_class = StorageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_company_owner:
            raise ValidationError("Только владелец компании может создавать склад.")
        if user.company is None:
            raise ValidationError("Пользователь не привязан к компании, склад создать нельзя.")
        if hasattr(user.company, 'storage'):
            raise ValidationError("У компании уже есть склад.")
        serializer.save(company=user.company)


class StorageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StorageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if user.company is None:
            raise ValidationError("Пользователь не привязан к компании.")
        if not hasattr(user.company, 'storage'):
            raise ValidationError("У компании нет склада.")
        return user.company.storage

    def perform_update(self, serializer):
        user = self.request.user
        if not user.is_company_owner:
            raise ValidationError("Только владелец компании может редактировать склад.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_company_owner:
            raise ValidationError("Только владелец компании может удалить склад.")
        instance.delete()


class SupplierListCreateView(generics.ListCreateAPIView):
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Supplier.objects.none()
        user = self.request.user
        if user is None or user.company is None:
            return Supplier.objects.none()
        return Supplier.objects.filter(company=user.company)

    def perform_create(self, serializer):
        user = self.request.user
        if user.company is None:
            raise ValidationError("Пользователь не привязан к компании.")
        serializer.save(company=user.company)


class SupplierRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Supplier.objects.none()
        user = self.request.user
        if user is None or user.company is None:
            return Supplier.objects.none()
        return Supplier.objects.filter(company=user.company)


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()
        user = self.request.user
        if user is None or user.company is None:
            return Product.objects.none()
        return Product.objects.filter(storage__company=user.company)

    def perform_create(self, serializer):
        user = self.request.user
        if user.company is None:
            raise ValidationError("Пользователь не привязан к компании.")
        serializer.save(quantity=0)


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()
        user = self.request.user
        if user is None or user.company is None:
            return Product.objects.none()
        return Product.objects.filter(storage__company=user.company)

    def perform_update(self, serializer):
        user = self.request.user
        if user.company is None:
            raise ValidationError("Пользователь не привязан к компании.")
        serializer.save()


class SupplyListCreateView(generics.ListCreateAPIView):
    serializer_class = SupplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Supply.objects.none()
        user = self.request.user
        if user is None or user.company is None:
            return Supply.objects.none()
        return Supply.objects.filter(company=user.company)

    def perform_create(self, serializer):
        user = self.request.user
        if user.company is None:
            raise ValidationError("Пользователь не привязан к компании.")
        serializer.save(company=user.company)


class AttachUserToCompanyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        owner = request.user
        if not owner.is_company_owner:
            return Response({"detail": "Только владелец компании может прикреплять пользователей."}, status=403)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"detail": "Необходимо указать user_id."}, status=400)

        try:
            user_to_attach = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден."}, status=404)

        if user_to_attach.company == owner.company:
            return Response({"detail": "Пользователь уже прикреплён к вашей компании."}, status=400)

        user_to_attach.company = owner.company
        user_to_attach.save()

        return Response({"detail": f"Пользователь {user_to_attach.email} успешно прикреплён к компании."})
