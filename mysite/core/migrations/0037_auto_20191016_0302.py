# Generated by Django 2.1.2 on 2019-10-16 03:02

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_auto_20191015_1608'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_id', models.CharField(default='', max_length=20)),
                ('last4', models.CharField(default='', max_length=4)),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.datetime(2019, 11, 15, 3, 2, 48, 162817, tzinfo=utc), null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='credit_cards',
            field=models.ManyToManyField(to='core.CreditCard'),
        ),
    ]
