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


class RestQuerySet(models.QuerySet):
    def fetch_with_map_point(self):
        for rest in self.all():
            if not rest.map_point:
                cords = fetch_coordinates(rest.address)
                lng, lat = cords
                point = Point.objects.create(lng=lng,
                                             lat=lat,
                                             address=rest.address)
                rest.map_point = point
                rest.save()

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
        prices = models.ExpressionWrapper(models.F('products__price') * models.F('products__quantity'),
                                          output_field=models.DecimalField(max_digits=8, decimal_places=2))

        return self.annotate(order_price=models.Sum(prices))

    def fetch_with_rest(self):
        rests_by_meal = dict()

        for order in self.all():
            if not order.restaurants.count():
                if not rests_by_meal:
                    for product in Product.objects.all():
                        rests_by_meal[product.id] = [m.restaurant.id for m in product.menu_items.all()]

                product_ents = order.products.all()
                possible_rests = [rests_by_meal[product_ent.product.id] for product_ent in product_ents]
                common_rests_id = list(reduce(lambda i, j: i & j, (set(x) for x in possible_rests)))
                common_rests = Restaurant.objects.filter(id__in=common_rests_id)
                order.restaurants.set(common_rests)
                order.save()

        return self

    def fetch_with_map_point(self):
        for order in self.all():
            if not order.map_point:
                cords = fetch_coordinates(order.address)
                if not cords:
                    return
                lng, lat = cords
                point = Point.objects.create(lng=lng,
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
                              related_name='products',
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







