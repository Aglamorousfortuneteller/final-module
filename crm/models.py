from django.contrib.auth.models import AbstractUser
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    inn = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return f"{self.name} (ИНН: {self.inn})"

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_company_owner = models.BooleanField(default=False)
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL, related_name='employees')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email




class Storage(models.Model):
    company = models.OneToOneField('Company', on_delete=models.CASCADE, related_name='storage')
    address = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.company.name} — склад: {self.address}"
