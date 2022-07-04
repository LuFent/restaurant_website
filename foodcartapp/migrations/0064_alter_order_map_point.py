# Generated by Django 3.2 on 2022-04-24 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cords', '0003_alter_point_creation_time'),
        ('foodcartapp', '0063_auto_20220424_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='map_point',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order', to='cords.point', verbose_name='Точка на карте'),
        ),
    ]
