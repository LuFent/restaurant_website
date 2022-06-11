# Generated by Django 3.2 on 2022-04-22 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0052_rename_reestaurant_order_restaurant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='restaurant',
        ),
        migrations.AddField(
            model_name='order',
            name='restaurants',
            field=models.ManyToManyField(db_index=True, null=True, to='foodcartapp.Restaurant', verbose_name='Ресторан'),
        ),
    ]
