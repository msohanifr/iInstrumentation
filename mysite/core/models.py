from datetime import timedelta

from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# base model_ver1
class Profile(models.Model):
    """
    Holds additional information about the user
    :param:
    user_email_verification: a flag for email verification.
                            0: verification has not started,
                            1: verification has been sent once
                            2: verification successful
    phone_verification_status: a flag for phone verification
                            0: verification has not started,
                            1: verification has been sent once,
                            2: verification successful
    :return:

    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verification_status = models.IntegerField(null=True, default=0)
    street1 = models.CharField(max_length=128, blank=False, default='')
    street2 = models.CharField(max_length=128, blank=True, default='')
    city = models.CharField(max_length=32, blank=False, default='')
    state = models.CharField(max_length=10, blank=False, default='')
    zip_code = models.CharField(blank=False, default='00000', max_length=12,
                                help_text="Zip code must be in XXXXX, 5 digit format")
    profile_filled = models.BooleanField(default=False)
    phone_regex = RegexValidator(regex=r'^[2-9]\d{2}-\d{3}-\d{4}$', message="Phone number must be entered in the "
                                                                            "format: 'XXX-XXX-XXXX'. Up to 15 digits "
                                                                            "allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=False,
                                    help_text="Phone number must be entered in the "
                                              "format: 'XXX-XXX-XXXX'. Up to 15 digits "
                                              "allowed.")  #
    phone_verification_code = models.IntegerField(default=0)
    phone_verification_status = models.IntegerField(default=0)
    number_of_sms_sent = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user.username + ':' + self.user.first_name + ' ' + self.user.last_name)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kmysqlwargs):
    instance.profile.save()


class Item(models.Model):
    """
    Model for sales items
    """
    title = models.CharField(max_length=32, null=True)  # The item name/title. This shows in one word what is the object
    price = models.DecimalField(default=0, decimal_places=2, max_digits=10)  # The price of this item.
    category = models.CharField(max_length=32,
                                default='Men')  # Category: Men, Women, Bottom, Top (Create a mixed list of these
    # values)
    description = models.CharField(max_length=128, default='')

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.description


class Service(models.Model):
    type = models.CharField(max_length=32, help_text='Service type', primary_key=True)
    description = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.type


# a vendor can sell many items
# an item might be sold by many Vendors
class Vendor(models.Model):
    """
    Model to keep vendor information

    """
    item = models.ManyToManyField(Item)
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def __str__(self):
        return self.profile.user.username


# a vendor can have many sales
class Order(models.Model):
    order_number = models.AutoField(primary_key=True, default=100000)
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
    )
    item = models.ManyToManyField(Item)
    delivered = models.BooleanField(default=False)
    purchase_date = models.DateField(null=True, default=timezone.now)
    delivery_date = models.DateField(null=True, default=timezone.now() + timedelta(days=30))
    number = models.IntegerField(default=0, help_text='Number of items sold')
    service = models.ManyToManyField(Service)
    client = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
    )
    last_status = models.CharField(null=True, default="", max_length=128)

    def __str__(self):
        return str(self.item.name) + ' ' + str(self.vendor.profile.user.username)


# keeps the coordinates for driver/package position on the map
class Position(models.Model):
    latitude = models.DecimalField(decimal_places=10, max_digits=13)
    longitude = models.DecimalField(decimal_places=10, max_digits=13)
