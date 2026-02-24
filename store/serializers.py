from decimal import Decimal
from rest_framework import serializers
from store.models import Product, Collection

# this will be external representation of the product model, the one in models.py is the internal representation (maybe there are some fields that we don't wanna expose to the client)
# API Model (interface) != Data Model (implementation)

class CollectionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Collection
    fields = ['id', 'title', 'products_count']

  products_count = serializers.IntegerField(read_only = True)

# class ProductSerializer(serializers.Serializer):
#   id = serializers.IntegerField()
#   title = serializers.CharField(max_length=255)
#   price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price') # name of the fields don't have to be the same as the model fields, but it's a good practice to keep them the same
#   price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
#   # collection = serializers.PrimaryKeyRelatedField(
#   #   queryset=Collection.objects.all()
#   # )
#   # OR
#   # collection = serializers.StringRelatedField()
#   # OR
#   # collection = CollectionSerializer()
#   # OR
#   collection = serializers.HyperlinkedRelatedField(
#     queryset=Collection.objects.all(),
#     view_name='collection-detail'
#   )

# OR

class ProductSerializer(serializers.ModelSerializer): # this enables us to not write the validations and all of the fields again in the serializer when they were already defined in the model
  class Meta:
    model = Product
    fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']

  price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
  

  def calculate_tax(self, product: Product):
    return product.unit_price * Decimal(1.1);

  # def create(self, validated_data): # helps to override the create method of the serializer
  #   product = Product(**validated_data) # ** is used to unpack the dictionary into keyword arguments
  #   product.other = 1
  #   product.save()
  #   return product

  # def update(self, instance, validated_data): # helps to override the update method of the serializer
  #   instance.unit_price = validated_data.get('unit_price')
  #   instance.save()
  #   return instance