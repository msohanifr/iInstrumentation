# Generated by Django 2.1.2 on 2019-10-18 18:19

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_auto_20191016_1722'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='payment_method',
        ),
        migrations.AddField(
            model_name='creditcard',
            name='expiry_month',
            field=models.CharField(default='', max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='creditcard',
            name='expiry_year',
            field=models.CharField(default='', max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.datetime(2019, 11, 17, 18, 19, 40, 912275, tzinfo=utc), null=True),
        ),
    ]