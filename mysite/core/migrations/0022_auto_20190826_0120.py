# Generated by Django 2.1.2 on 2019-08-26 01:20

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20190826_0120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.datetime(2019, 9, 25, 1, 20, 22, 683466, tzinfo=utc), null=True),
        ),
    ]
