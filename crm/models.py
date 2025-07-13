from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class Company(models.Model):
    name = models.CharField(max_length=255)
    inn = models.CharField(max_length=12, unique=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return f"{self.name} (ИНН: {self.inn})"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_company_owner = models.BooleanField(default=False)
    company = models.ForeignKey('Company', null=True, blank=True, on_delete=models.SET_NULL, related_name='employees')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Storage(models.Model):
    company = models.OneToOneField('Company', on_delete=models.CASCADE, related_name='storage')
    address = models.CharField(max_length=255)

    def __str__(self):
        company_name = self.company.name if self.company else "Без компании"
        return f"{company_name} — склад: {self.address}"


class Supplier(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='suppliers')
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class Product(models.Model):
    storage = models.ForeignKey('Storage', on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=0)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.title} ({self.quantity})"


class Supply(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='supplies')
    date = models.DateTimeField(auto_now_add=True)
    supplier = models.ForeignKey('Supplier', on_delete=models.PROTECT, related_name='supplies')

    def __str__(self):
        return f"Supply {self.id} from {self.supplier.name} ({self.date})"


class SupplyProduct(models.Model):
    supply = models.ForeignKey('Supply', on_delete=models.CASCADE, related_name='supply_products')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='supply_products')
    quantity = models.PositiveIntegerField()

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Количество товара в поставке должно быть положительным.")

    def __str__(self):
        return f"{self.product.title} - {self.quantity} pcs in supply {self.supply.id}"
