from django.contrib import admin
from mysite.core.models import Profile, Vendor, Item, Order, Service

# Register your models here.

admin.site.register(Profile)
admin.site.register(Vendor)
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Service)
