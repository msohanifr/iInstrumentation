# Generated by Django 2.1.2 on 2019-08-21 16:51

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_auto_20190821_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.datetime(2019, 9, 20, 16, 51, 42, 247170, tzinfo=utc), null=True),
        ),
    ]
