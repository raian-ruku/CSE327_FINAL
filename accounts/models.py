from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import base64

class Meta:
    app_label = 'accounts'

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class WebUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(username, email, password, **extra_fields)


class WebUser(AbstractBaseUser):
    USER_TYPE_CHOICES = [
        ('', 'Select User Type'),
        ('owner', 'Owner'),
        ('tenant', 'Tenant'),
        ('renter', 'Renter'),
    ]
    
    username = models.CharField(max_length=150, unique=True, default='defaultuser')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=254)
    user_type = models.CharField(max_length=30, choices=USER_TYPE_CHOICES, default='')
    owner_unique_id = models.CharField(max_length=30, blank=True)
    owner_id = models.CharField(max_length=30, blank=True)
    nid = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    files = models.FileField(upload_to='files/', blank=True, null=True)  # Add this field

 

    objects = WebUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class Apartment(models.Model):
    owner = models.ForeignKey(WebUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    area = models.CharField(max_length=255)
    bedrooms = models.PositiveIntegerField()
    washrooms = models.PositiveIntegerField()
    description = models.TextField()
    short_description = models.CharField(max_length=255)
    is_vacant = models.BooleanField(default=True)
   

   

    def __str__(self):
        return self.address


class Tenant(models.Model):
    user = models.OneToOneField(WebUser, on_delete=models.CASCADE, related_name='tenant')
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    # Add additional fields as per your requirements


class MaintenanceRequest(models.Model):
    tenant = models.ForeignKey(WebUser, on_delete=models.CASCADE, related_name='maintenance_requests')
    owner = models.ForeignKey(WebUser, on_delete=models.CASCADE, related_name='owner_requests')
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

class Chat(models.Model):
    owner = models.ForeignKey(WebUser, on_delete=models.CASCADE, related_name='owner_chats')
    tenant = models.ForeignKey(WebUser, on_delete=models.CASCADE, related_name='tenant_chats')
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(WebUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Message #{self.id}"
    
class Visit(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=20)
    email = models.EmailField()
    nid_number = models.CharField(max_length=20)
    visit_date = models.DateField()
    visit_time = models.TimeField()

    def __str__(self):
        return f"Visit for {self.apartment.address} by {self.name}"