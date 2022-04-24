from django.db import models
from django.utils import timezone


class Point(models.Model):
    lat = models.FloatField(verbose_name='Ширтоа')
    lng = models.FloatField(verbose_name='Долгота')
    creation_time = models.DateTimeField(default=timezone.now, verbose_name='Время создания')
    address = models.CharField(max_length=100, verbose_name='Адресс')

    def __str__(self):
        if self.rest.all():
            return f'Точка для ресторана {self.rest.first()}'
        else:
            return f'Точка для места заказа {self.order.first()}'



