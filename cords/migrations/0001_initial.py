# Generated by Django 3.2 on 2022-04-24 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.FloatField(verbose_name='Ширтоа')),
                ('lng', models.FloatField(verbose_name='Долгота')),
                ('creation_time', models.DateTimeField(verbose_name='Время создания')),
                ('address', models.CharField(max_length=100, verbose_name='Адресс')),
            ],
        ),
    ]
