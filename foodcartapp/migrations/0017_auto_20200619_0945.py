# Generated by Django 3.0.7 on 2020-06-19 09:45

from django.db import migrations


def fill_new_admin_field(apps, schema_editor):
    Restaurant = apps.get_model("foodcartapp", "Restaurant")
    for restaurant in Restaurant.objects.all():
        restaurant.new_admin = restaurant.admin.user
        restaurant.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0016_restaurant_new_admin'),
    ]

    operations = [
        migrations.RunPython(fill_new_admin_field),
    ]
