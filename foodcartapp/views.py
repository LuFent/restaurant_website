import json

from .models import Product, ProductEntity, Order
from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from phonenumbers import parse, is_valid_number
from phonenumbers.phonenumberutil import NumberParseException
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import CharField, IntegerField, SlugRelatedField, ListField, ModelSerializer

from django.core.validators import MinValueValidator

def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class ProductEntitySerializer(ModelSerializer):
    product = SlugRelatedField(slug_field='id', queryset=Product.objects.all())
    quantity = IntegerField(validators = [MinValueValidator(1)])
    class Meta:
        model = ProductEntity
        fields = ['quantity', 'product']


class OrderSerializer(ModelSerializer):
    products = ProductEntitySerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['phonenumber', 'lastname', 'firstname', 'address', 'products']


@transaction.atomic
@api_view(['POST'])
def register_order(request):

    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)  # ?????????????? ValidationError

    order = Order.objects.create(
        address=serializer.validated_data['address'],
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
    )
    product_fields = serializer.validated_data['products']
    products = [ProductEntity(order=order,
                              product=fields['product'],
                              quantity=fields['quantity'],
                              price=fields['product'].price)
                for fields in product_fields]
    ProductEntity.objects.bulk_create(products)
    return Response({**dict(serializer.data), 'id': order.id})
