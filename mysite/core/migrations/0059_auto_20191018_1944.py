# Generated by Django 2.1.2 on 2019-10-18 19:44

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0058_auto_20191018_1934'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='credit_cards',
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.datetime(2019, 11, 17, 19, 44, 57, 112245, tzinfo=utc), null=True),
        ),
    ]
