# Generated by Django 2.1.2 on 2019-10-16 03:02

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20191016_0302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.datetime(2019, 11, 15, 3, 2, 51, 393384, tzinfo=utc), null=True),
        ),
    ]
