# Generated by Django 3.0.7 on 2020-06-19 08:38

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foodcartapp', '0002_auto_20200619_0836'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CustomUser',
            new_name='Customer',
        ),
    ]
