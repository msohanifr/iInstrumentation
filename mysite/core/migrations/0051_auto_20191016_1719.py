# Generated by Django 2.1.2 on 2019-10-16 17:19

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_auto_20191016_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='vendor_name',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.datetime(2019, 11, 15, 17, 19, 9, 236173, tzinfo=utc), null=True),
        ),
    ]
