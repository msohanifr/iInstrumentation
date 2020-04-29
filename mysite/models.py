from datetime import timedelta, date

from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# keeps the coordinates position on the map
class Position(models.Model):
    latitude = models.DecimalField(decimal_places=10, max_digits=13)
    longitude = models.DecimalField(decimal_places=10, max_digits=13)

    def __str__(self):
        return str(self.latitude) + ',' + str(self.longitude)


# base model_ver1
class Profile(models.Model):
    """
    Holds additional information about the user
    :param:
    user_email_verification: a flag for email verification.
                            0: verification has not started,
                            1: XX
                            2: verification successful
    phone_verification_status: a flag for phone verification
                            0: verification has not started,
                            1: XX,
                            2: verification successful
    :return:

    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.OneToOneField(Position, on_delete=models.CASCADE, primary_key=False, null=True)
    email_verification_status = models.IntegerField(null=True, default=0)
    street1 = models.CharField(max_length=128, blank=False, default='')
    street2 = models.CharField(max_length=128, blank=True, default='')
    city = models.CharField(max_length=32, blank=False, default='')
    STATES = (
        ('NJ', 'Newjersey'),
    )
    state = models.CharField(max_length=2, blank=False, default='', choices=STATES)
    zip_code = models.CharField(blank=False, default='', max_length=5,
                                help_text="Zip code must be in XXXXX, 5 digit format")
    profile_filled = models.BooleanField(default=False)
    phone_regex = RegexValidator(regex=r'^[2-9]\d{2}-\d{3}-\d{4}$', message="Phone number must be entered in the "
                                                                            "format: 'XXX-XXX-XXXX'. Up to 15 digits "
                                                                            "allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=12, blank=False,
                                    help_text="Phone number must be entered in the "
                                              "format: 'XXX-XXX-XXXX'. Up to 15 digits "
                                              "allowed.")  #
    phone_verification_code = models.IntegerField(default=0)
    phone_verification_status = models.IntegerField(default=0)
    number_of_sms_sent = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    customer_id = models.CharField(max_length=32, default='', null=True, blank=True)

    def __str__(self):
        return str(self.user.username + ':' + self.user.first_name + ' ' + self.user.last_name)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kmysqlwargs):
    instance.profile.save()


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
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    #  Vendor.objects.filter(supporting_zip_codes__contains=[7932])
    supporting_zip_codes = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    rating = models.IntegerField(null=True)  # Rating for the vendor
    pricing = models.IntegerField(null=True)  # Rating for pricing
    customers = models.ManyToManyField(User, blank=True)  # customers for this Vendor
    hours = models.CharField(max_length=512, blank=True, null=True, default='')
    delivery_notes = models.CharField(max_length=512, blank=True, null=True, default='')
    services = models.CharField(max_length=512, blank=True, null=True)
    photo = models.CharField(default='images/shop/', max_length=32, null=True)

    def __str__(self):
        return self.profile.user.username


class Item(models.Model):
    """
    Model for sales items
    """
    title = models.CharField(max_length=32, null=True)  # The item name/title. This shows in one word what is the object
    category = models.CharField(max_length=32,
                                default='Men')  # Category: Men, Women, Bottom, Top (Create a mixed list of these
    # values)
    description = models.CharField(max_length=128, default='')
    photo = models.CharField(default='images/', max_length=32, null=True)
    price = models.DecimalField(null=True, decimal_places=2, max_digits=12)
    vendor = models.ForeignKey(Vendor, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "Title:" + str(self.title)


# a vendor can have many sales
class Order(models.Model):
    order_number = models.AutoField(primary_key=True)
    item = models.ManyToManyField(Item)
    delivered = models.BooleanField(default=False)
    purchase_date = models.DateField(null=True, blank=True)
    pickup_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    service = models.ManyToManyField(Service)
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    STATUSES = (
        ('OR', 'Order Received'),
        ('PS', 'Pickup Scheduled'),
        ('PU', 'Picked Up and In Process'),
        ('DS', 'Delivery Scheduled'),
        ('DV', 'Delivered'),
    )
    last_status = models.CharField(null=True, default="", max_length=2, choices=STATUSES)
    price = models.DecimalField(null=True, default=0, max_digits=10, decimal_places=2)
    price_confirmed = models.BooleanField(null=True, default=False)
    order_disabled = models.BooleanField(null=True, default=False)

    def __str__(self):
        return str(self.pk)

    @classmethod
    def create(cls):
        order = cls()
        order.purchase_date = date.today()
        # do something with the book
        return order
