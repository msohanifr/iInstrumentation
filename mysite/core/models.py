from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# base model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    street1 = models.CharField(max_length=128, blank=False, default='')
    street2 = models.CharField(max_length=128, blank=True, default='')
    city = models.CharField(max_length=32, blank=False, default='')
    state = models.CharField(max_length=10, blank=False, default='')
    zip_code = models.CharField(blank=False, default=0, max_length=12)
    birth_date = models.DateField(null=True, blank=False, default=timezone.now)
    profile_filled = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.username + ':' + self.user.first_name + ' ' + self.user.last_name)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# ------------- Sales ---------------
# Purchases : -----------------------
class Item(models.Model):
    title = models.CharField(max_length=32, null=True) # The item name/title. This shows in one word what is the object
    price = models.DecimalField(default=0, decimal_places=2, max_digits=10) # The price of this item.
    category = models.CharField(max_length=32, default='Men') # Category: Men, Women, Bottom, Top (Create a mixed list of these values)
    description = models.CharField(max_length=128, default='')
    image = models.ImageField(null=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class Service(models.Model):
    type = models.CharField(max_length=32, help_text='Service type', primary_key=True)
    description = models.CharField(max_length=128, null=True)

    def __str__(self):
        return type


# a vendor can sell many items
# an item might be sold by many Vendors
class Vendor(models.Model):
    item = models.ManyToManyField(Item)
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def __str__(self):
        return self.profile.user.username


# a vendor can have many sales
class Sale(models.Model):
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
    )
    item = models.ManyToManyField(Item)
    purchase_date = models.DateField(null=False, default=timezone.now)
    number = models.IntegerField(default=0, help_text='Number of items sold')
    service = models.ManyToManyField(Service)
    client = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.item.name) + ' ' + str(self.vendor.profile.user.username)


# keeps the coordinates for driver/package position on the map
class Position(models.Model):
    latitude = models.DecimalField(decimal_places=10, max_digits=13)
    longitude = models.DecimalField(decimal_places=10, max_digits=13)
