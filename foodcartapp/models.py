from cords.models import Point
from cords.views import fetch_coordinates
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.core.validators import MinValueValidator, BaseValidator
from django.db import models
from django.db.models import F, Count
from django.utils import timezone
from functools import reduce
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Prefetch


class RestQuerySet(models.QuerySet):
    def fetch_with_map_point(self):
        for restaurant in self:
            if restaurant.map_point and restaurant.map_point.lat and restaurant.map_point.lng:
                continue

            cords = fetch_coordinates(restaurant.address)
            if not cords:
                lng, lat = None, None

            lng, lat = cords
            point, _ = Point.objects.get_or_create(lng=lng,
                                                lat=lat,
                                                address=restaurant.address)
            restaurant.map_point = point
            restaurant.save()

        return self


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )
    map_point = models.ForeignKey(Point,
                                  verbose_name="Точка на карте",
                                  related_name="rest",
                                  null=True,
                                  blank=True,
                                  on_delete=models.CASCADE)

    objects = RestQuerySet.as_manager()

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )
    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def fetch_with_order_price(self):
        prices = models.ExpressionWrapper(models.F('products_entities__price') * models.F('products_entities__quantity'),
                                          output_field=models.DecimalField(max_digits=8, decimal_places=2))

        return self.annotate(order_price=models.Sum(prices))

    def fetch_with_rest(self):
        restaurants_by_meal = dict()
        for product in Product.objects.prefetch_related(Prefetch('menu_items',
                     queryset=RestaurantMenuItem.objects.filter(availability=True).
                         select_related('restaurant', 'restaurant__map_point'))):

            restaurants_by_meal[product.id] = [m.restaurant for m in product.menu_items.all()]

        for order in self:
            product_entities = order.products_entities.all()
            products_restaurants = [restaurants_by_meal[product_entity.product.id] for product_entity in product_entities]
            common_restaurants = set.intersection(*map(set, products_restaurants))
            order.possible_restaurants = common_restaurants
        return self


    def fetch_with_map_point(self):
        for order in self:
            if order.map_point and order.map_point.lat and order.map_point.lng:
                continue
            cords = fetch_coordinates(order.address)
            if not cords:
                lng, lat = None, None
            else:
                lng, lat = cords

            point, cre = Point.objects.get_or_create(lng=lng,
                                         lat=lat,
                                         address=order.address)
            order.map_point = point
            order.save()


class Order(models.Model):
    status = models.CharField(default='unprocessed',
                              verbose_name='статус заказа',
                              max_length=25,
                              db_index=True,
                              choices=[('processed', 'Обработан'),
                                       ('unprocessed', 'Не обработан')])

    payment_method = models.CharField(default='unknown',
                                      verbose_name='способ оплаты',
                                      max_length=25,
                                      db_index=True,
                                      choices=[('cash', 'Наличные'),
                                               ('card', 'Электронно'),
                                               ('unknown', 'Не указано')])

    address = models.CharField(max_length=100, verbose_name='Адрес')
    firstname = models.CharField(max_length=50, verbose_name='Имя')
    lastname = models.CharField(max_length=50, verbose_name='Фамилия')
    phonenumber = PhoneNumberField(db_index=True, verbose_name='Номер телефона')
    comment = models.TextField(blank=True,
                               verbose_name='коментарий к заказу', )

    registration_time = models.DateTimeField(default=timezone.now,
                                             verbose_name='Время регистрации заказа',
                                             db_index=True)

    call_time = models.DateTimeField(null=True,
                                     blank=True,
                                     verbose_name='Время звонка менеджера',
                                     db_index=True)

    delivery_time = models.DateTimeField(null=True,
                                         blank=True,
                                         verbose_name='Время доставки',
                                         db_index=True)

    map_point = models.ForeignKey(Point, verbose_name="Точка на карте",
                                  related_name="order",
                                  null=True,
                                  blank=True,
                                  on_delete=models.CASCADE)

    restaurants = models.ManyToManyField(Restaurant,
                                         blank=True,
                                         verbose_name='Ресторан')

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ {self.id}'


class ProductEntity(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                verbose_name='Продукт',
                                related_name='entities')

    order = models.ForeignKey(Order,
                              related_name='products_entities',
                              on_delete=models.CASCADE,
                              verbose_name='Заказ')

    quantity = models.IntegerField(verbose_name='Кол-во')

    price = models.DecimalField(verbose_name='Цена позиции',
                                max_digits=7,
                                decimal_places=2,
                                validators=[MinValueValidator(0.0)])

    class Meta:
        verbose_name = 'заказаннй продукт'
        verbose_name_plural = 'заказанные продукты'

    def __str__(self):
        return f'{self.quantity} единицы "{self.product.name}" для заказа {self.order.id}'







