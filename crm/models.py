from django.contrib.auth.models import AbstractUser
from django.db import models

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

