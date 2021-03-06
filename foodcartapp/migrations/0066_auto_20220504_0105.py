# Generated by Django 3.2 on 2022-05-03 22:05

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0065_alter_restaurant_map_point'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(max_length=100, verbose_name='Адрес'),
        ),
        migrations.AlterField(
            model_name='productentity',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_entities', to='foodcartapp.order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='productentity',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Цена позиции'),
        ),
    ]
