from rest_framework import serializers
from .models import User, Company, Storage, Supplier, Product, SupplyProduct, Supply
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'inn']


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = ['id', 'company', 'address']
        read_only_fields = ['company']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'company', 'name', 'contact_info']
        read_only_fields = ['company']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'storage', 'title', 'quantity', 'purchase_price']
        read_only_fields = ['quantity']


class SupplyProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = SupplyProduct
        fields = ['id', 'product', 'product_id', 'quantity']


class SupplySerializer(serializers.ModelSerializer):
    supply_products = SupplyProductSerializer(many=True)

    class Meta:
        model = Supply
        fields = ['id', 'company', 'date', 'supplier', 'supply_products']
        read_only_fields = ['company', 'date']

    def create(self, validated_data):
        supply_products_data = validated_data.pop('supply_products')
        company = self.context['request'].user.company
        if company is None:
            raise serializers.ValidationError("Пользователь не привязан к компании.")
        validated_data['company'] = company
        supply = Supply.objects.create(**validated_data)

        for item in supply_products_data:
            product_id = item.get('product_id')
            quantity = item.get('quantity')

            if quantity <= 0:
                raise serializers.ValidationError("Количество товара должно быть положительным.")

            try:
                product = Product.objects.get(id=product_id, storage__company=company)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Товар с id {product_id} не найден или не принадлежит вашей компании.")

            SupplyProduct.objects.create(supply=supply, product=product, quantity=quantity)

            product.quantity += quantity
            product.save()

        return supply
