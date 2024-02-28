from django.contrib import admin

from .models import User, Customer, Driver, Manager

# Register your models here.
admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Driver)
admin.site.register(Manager)
