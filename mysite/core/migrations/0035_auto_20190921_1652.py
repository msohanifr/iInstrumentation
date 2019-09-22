# Generated by Django 2.1.2 on 2019-09-21 16:52

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20190921_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.datetime(2019, 10, 21, 16, 52, 42, 399892, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='state',
            field=models.CharField(choices=[('NJ', 'Newjersey')], default='', max_length=2),
        ),
    ]
