# Generated by Django 3.2 on 2022-04-22 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20220422_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='call_time',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Время звонка менеджера'),
        ),
    ]
