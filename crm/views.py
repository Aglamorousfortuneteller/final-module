from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from .models import User, Company, Storage
from .serializers import RegisterSerializer, CompanySerializer, StorageSerializer


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
        print(f"User after save: {user}, company: {user.company}, is_owner: {user.is_company_owner}")


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
        # Обнуляем связи у пользователя
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
