# Generated by Django 2.1.2 on 2019-09-19 17:05

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0031_auto_20190919_1646'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='photo',
            new_name='_photo',
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.datetime(2019, 10, 19, 17, 5, 46, 936477, tzinfo=utc), null=True),
        ),
    ]
