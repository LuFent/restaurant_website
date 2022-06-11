# Generated by Django 3.2 on 2022-04-22 08:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_auto_20220422_1140'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_time',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Время доставки'),
        ),
        migrations.AddField(
            model_name='order',
            name='registration_time',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Время регистрации заказа'),
        ),
    ]
