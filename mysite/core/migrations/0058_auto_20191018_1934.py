# Generated by Django 2.1.2 on 2019-10-18 19:34

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0057_auto_20191018_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.datetime(2019, 11, 17, 19, 34, 41, 857492, tzinfo=utc), null=True),
        ),
    ]