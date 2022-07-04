# Generated by Django 3.0.7 on 2020-07-03 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0030_auto_20200629_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='address',
            field=models.CharField(blank=True, max_length=100, verbose_name='адрес'),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=50, verbose_name='контактный телефон'),
        ),
    ]
