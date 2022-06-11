# Generated by Django 3.0.7 on 2020-06-19 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0019_auto_20200619_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(choices=[(1, 'новый'), (2, 'подтверждён'), (3, 'готовится'), (4, 'в пути'), (5, 'доставлен'), (6, 'отменён')], db_index=True, default=1, verbose_name='статус'),
        ),
    ]
