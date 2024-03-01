from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150, null=True, blank=True, verbose_name=_("first name"))
    last_name = models.CharField(max_length=150, null=True, blank=True, verbose_name=_("last name"))
    username = models.CharField(max_length=150, unique=True, null=True, blank=True, verbose_name=_("username"))
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True, verbose_name=_("email"))

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    is_driver = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# Customer models
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    customer_id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("first name"))
    last_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("last name"))
    username = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("username"))
    email = models.EmailField(max_length=255, null=True, blank=True, verbose_name=_("email"))
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("phone number"))
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("address"))
    profile_image = models.ImageField(upload_to='profiles/customer/', null=True, blank=True, verbose_name=_("profile picture"))

    def __str__(self):
        return str(self.username)

# Driver models
class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    driver_id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("first name"))
    last_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("last name"))
    username = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("username"))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("date of birth"))
    email = models.EmailField(max_length=255, null=True, blank=True, verbose_name=_("email"))
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("phone number"))
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("address"))
    id_card = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("identification card"))
    driver_license = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("driving license"))
    profile_image = models.ImageField(upload_to='profiles/driver/', null=True, blank=True, verbose_name=_("profile picture"))

    def __str__(self):
        return str(self.username)
