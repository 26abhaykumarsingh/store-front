from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Collection, Product
from .serializers import CollectionSerializer, ProductSerializer

# Create your views here.

@api_view(['GET', 'POST']) # if we apply this decorator to a view, the request object that we receive will be instance of the request class from rest framework instead of request object from django; this is useful because rest framework provides additional features like parsing the request body, validating the request data, etc.
def product_list(request):
  # return HttpResponse('Hello, World!') # this is the old way of returning response which uses django's HttpResponse class
  # return Response('ok') # this is the new way of returning response which uses rest framework's Response class
  if request.method == 'GET':
    queryset = Product.objects.select_related('collection').all()
    serializer = ProductSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)
  elif request.method == 'POST':
    serializer = ProductSerializer(data=request.data)
    # if serializer.is_valid():
    #   serializer.validated_data
    #   return Response('ok')
    # else:
    #   return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # OR
    serializer.is_valid(raise_exception=True)
    serializer.save()
    print(serializer.validated_data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, id):
  product = get_object_or_404(Product, pk=id)
  if request.method == 'GET':
    # try:
    #   product = Product.objects.get(pk=id)
    #   serializer = ProductSerializer(product) # Rest framework has JSONRenderer class which has render(dict) method which takes dictionary object and returns json object. Serializer is an object that knows how to convert a model instance to a python dictionary
    #   return Response(serializer.data) # serializer.data is a dictionary that contains the serialized data of the product
    # except Product.DoesNotExist:
    #   return Response(status=status.HTTP_404_NOT_FOUND)
    # ALTERNATE TO ABOVE CODE:
    # product = get_object_or_404(Product, pk=id) this line is moved outside of if
    serializer = ProductSerializer(product) # Rest framework has JSONRenderer class which has render(dict) method which takes dictionary object and returns json object. Serializer is an object that knows how to convert a model instance to a python dictionary
    return Response(serializer.data) # serializer.data is a dictionary that contains the serialized data of the product
  elif request.method == 'PUT':
    serializer = ProductSerializer(product,data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
  elif request.method == 'DELETE':
    if product.orderitems.count() > 0:
      return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def collection_list(request):
  if request.method == 'GET':
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer = CollectionSerializer(queryset, many=True)
    return Response(serializer.data)
  elif request.method == 'POST':
    serializer = CollectionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
  collection = get_object_or_404(
    Collection.objects.annotate(
      products_count = Count('products')), pk=pk)
  if request.method == 'GET':
    serializer = CollectionSerializer(collection)
    return Response(serializer.data)
  elif request.method == 'PUT':
    serializer = CollectionSerializer(collection, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
  elif request.method == 'DELETE':
    if collection.products.count() > 0:
      return Response({'error': 'Collection cannot be deleted because it is associated with a product.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    collection.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)