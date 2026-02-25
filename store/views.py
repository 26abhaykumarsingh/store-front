from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from store.filters import ProductFilter
from .models import Collection, OrderItem, Product, Review
from .serializers import CollectionSerializer, ProductSerializer, ReviewSerializer

# Create your views here.

class ProductViewSet(ModelViewSet): # this is alternate to using ListCreateAPIView and RetrieveUpdateDestroyAPIView classes
  queryset = Product.objects.all() # since we removed this queryset from here we have to explicitly define basename in the urls.py
  serializer_class = ProductSerializer
  filter_backends = [DjangoFilterBackend]
  # filterset_fields = ['collection_id', 'unit_price']
  filterset_class = ProductFilter

  # def get_queryset(self): # this isn't needed now since we using django-filter library now
  #   queryset = Product.objects.all()
  #   collection_id = self.request.query_params.get('collection_id')
  #   if collection_id is not None:
  #     queryset = queryset.filter(collection_id=collection_id)
  #   return queryset

  def get_serializer_context(self):
    return {'request': self.request}

  def destroy(self, request, *args, **kwargs):
    if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
      return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):
  queryset = Collection.objects.annotate(products_count=Count('products')).all()
  serializer_class = CollectionSerializer

  def destroy(self, request, *args, **kwargs):
    if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
      return Response({'error': 'Collection cannot be deleted because it is associated with a product.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return super().destroy(request, *args, **kwargs)

class ReviewViewSet(ModelViewSet):
  # queryset = Review.objects.all()
  serializer_class = ReviewSerializer

  def get_queryset(self):
    return Review.objects.filter(product_id=self.kwargs['product_pk'])

  def get_serializer_context(self):
    return {'product_id': self.kwargs['product_pk']}


# class ProductList(ListCreateAPIView):
#   queryset = Product.objects.all()
#   serializer_class = ProductSerializer
  
#   # def get_queryset(self): # if we have any special logic we can use these functions, otherwise we can also use the attributes of the class
#   #   return Product.objects.select_related('collection').all()

#   # def get_serializer_class(self):
#   #   return ProductSerializer

#   def get_serializer_context(self):
#     return {'request': self.request}

# class ProductList(APIView): # this was alternate to function based view using APIView class. but we can reduce repetition in code using generic classes which inherits mixins which actually have all the code that needs to be written again and again in them
#   def get(self, request):
#     queryset = Product.objects.select_related('collection').all()
#     serializer = ProductSerializer(queryset, many=True, context={'request': request})
#     return Response(serializer.data)
    
#   def post(self, request):
#     serializer = ProductSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data, status=status.HTTP_201_CREATED)

# class ProductDetail(RetrieveUpdateDestroyAPIView):
#   queryset = Product.objects.all()
#   serializer_class = ProductSerializer

#   def delete(self, request, pk): # override the delete method to handle the case when product is associated with an order item
#     product = get_object_or_404(Product, pk=pk)
#     if product.orderitems.count() > 0:
#       return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#     product.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)


# class ProductDetail(APIView):
#   def get(self, request, id):
#     product = get_object_or_404(Product, pk=id)
#     serializer = ProductSerializer(product) # Rest framework has JSONRenderer class which has render(dict) method which takes dictionary object and returns json object. Serializer is an object that knows how to convert a model instance to a python dictionary
#     return Response(serializer.data)
  
#   def put(self, request, id):
#     product = get_object_or_404(Product, pk=id)
#     serializer = ProductSerializer(product,data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data)

#   def delete(self, request, id):
#     product = get_object_or_404(Product, pk=id)
#     if product.orderitems.count() > 0:
#       return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#     product.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET', 'POST']) # if we apply this decorator to a view, the request object that we receive will be instance of the request class from rest framework instead of request object from django; this is useful because rest framework provides additional features like parsing the request body, validating the request data, etc.
# def product_list(request):
#   # return HttpResponse('Hello, World!') # this is the old way of returning response which uses django's HttpResponse class
#   # return Response('ok') # this is the new way of returning response which uses rest framework's Response class
#   if request.method == 'GET':
#     queryset = Product.objects.select_related('collection').all()
#     serializer = ProductSerializer(queryset, many=True, context={'request': request})
#     return Response(serializer.data)
#   elif request.method == 'POST':
#     serializer = ProductSerializer(data=request.data)
#     # if serializer.is_valid():
#     #   serializer.validated_data
#     #   return Response('ok')
#     # else:
#     #   return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     # OR
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     print(serializer.validated_data)
#     return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(['GET', 'PUT', 'DELETE'])
# def product_detail(request, id):
#   product = get_object_or_404(Product, pk=id)
#   if request.method == 'GET':
#     # try:
#     #   product = Product.objects.get(pk=id)
#     #   serializer = ProductSerializer(product) # Rest framework has JSONRenderer class which has render(dict) method which takes dictionary object and returns json object. Serializer is an object that knows how to convert a model instance to a python dictionary
#     #   return Response(serializer.data) # serializer.data is a dictionary that contains the serialized data of the product
#     # except Product.DoesNotExist:
#     #   return Response(status=status.HTTP_404_NOT_FOUND)
#     # ALTERNATE TO ABOVE CODE:
#     # product = get_object_or_404(Product, pk=id) this line is moved outside of if
#     serializer = ProductSerializer(product) # Rest framework has JSONRenderer class which has render(dict) method which takes dictionary object and returns json object. Serializer is an object that knows how to convert a model instance to a python dictionary
#     return Response(serializer.data) # serializer.data is a dictionary that contains the serialized data of the product
#   elif request.method == 'PUT':
#     serializer = ProductSerializer(product,data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data)
#   elif request.method == 'DELETE':
#     if product.orderitems.count() > 0:
#       return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#     product.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)

# class CollectionList(ListCreateAPIView):
#   queryset = Collection.objects.annotate(products_count=Count('products')).all()
#   serializer_class = CollectionSerializer

# @api_view(['GET', 'POST'])
# def collection_list(request):
#   if request.method == 'GET':
#     queryset = Collection.objects.annotate(products_count=Count('products')).all()
#     serializer = CollectionSerializer(queryset, many=True)
#     return Response(serializer.data)
#   elif request.method == 'POST':
#     serializer = CollectionSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data, status=status.HTTP_201_CREATED)

# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#   queryset = Collection.objects.annotate(products_count=Count('products')).all()
#   serializer_class = CollectionSerializer

#   def delete(self, request, pk):
#     collection = get_object_or_404(Collection, pk=pk)
#     if collection.products.count() > 0:
#       return Response({'error': 'Collection cannot be deleted because it is associated with a product.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#     collection.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET', 'PUT', 'DELETE'])
# def collection_detail(request, pk):
#   collection = get_object_or_404(
#     Collection.objects.annotate(
#       products_count = Count('products')), pk=pk)
#   if request.method == 'GET':
#     serializer = CollectionSerializer(collection)
#     return Response(serializer.data)
#   elif request.method == 'PUT':
#     serializer = CollectionSerializer(collection, data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data)
#   elif request.method == 'DELETE':
#     if collection.products.count() > 0:
#       return Response({'error': 'Collection cannot be deleted because it is associated with a product.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#     collection.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)







# for building api there are 3 steps:
# 1. Create a serializer
# 2. Create a view
# 3. Register a route