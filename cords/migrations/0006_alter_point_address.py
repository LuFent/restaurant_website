# Generated by Django 3.2 on 2022-05-24 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cords', '0005_auto_20220504_2111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='point',
            name='address',
            field=models.CharField(max_length=100, unique=True, verbose_name='Адрес'),
        ),
    ]
