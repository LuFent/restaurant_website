# Generated by Django 3.2 on 2022-04-21 14:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_productentity_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productentity',
            name='price',
            field=models.DecimalField(decimal_places=10, max_digits=19, null=True, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Цена позиции'),
        ),
    ]
