from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, connection
from django.db.models import Value, Q, F, Func, ExpressionWrapper, DecimalField # Q for Query; Q object is used to build complex queries using &, |, ~ operators; F object is used to reference fields in the model
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from store.models import Customer, Product, Collection
from store.models import OrderItem
from store.models import Order
from tags.models import TaggedItem

# @transaction.atomic() # decorator is used to make the entire view atomic, if any error occurs, all changes will be rolled back
def say_hello(request):
    # query_set = Product.objects.all() # every model has an attribute called object which is a manager object which is interface to database, its a remote with buttons we can use to talk to database; query set is an object which encapsultes a query which will be evaluated by django and generate sql statement to sent to our database
    # all returns query set but .get(pk=1) returns a single object, pk is special argument for primary key
    try:
        product = Product.objects.get(pk=0)
    except ObjectDoesNotExist:
        pass
    # to not get error without try except, we can use filter and first which returns none if no object is found
    product = Product.objects.filter(pk=0).first()
    exists = Product.objects.filter(pk=0).exists()
    queryset = Product.objects.filter(unit_price__gt=20) # we can't use (unit_price > 20) here as it will return boolean. so we have lookup types in queryset like __gt, __lt, __gte, __lte, __eq, __ne, __in, __not_in, __isnull, __isnotnull, __startswith, __endswith, __contains, __icontains, __regex, __iregex
    queryset1 = Product.objects.filter(unit_price__range=(20, 30))
    queryset2 = Product.objects.filter(collection__id__range=(1, 2, 3)) # this is foreign key lookup
    queryset3 = Product.objects.filter(title__icontains='coffee') # this is string lookup, __contains is case sensitive, __icontains is case insensitive, other string lookups are __startswith, __endswith, __contains, and their case insensitive versions
    queryset4 = Product.objects.filter(last_update__year=2021) # this is date lookup, __year, __month, __day, __week_day, __hour, __minute, __second, __microsecond, __week, __iso_year, __iso_week_day 
    queryset5 = Product.objects.filter(description__isnull=True) # this is boolean lookup, __isnull, __isnotnull

    # COMPLEX LOOKUPS
    queryset6 = Product.objects.filter(inventory__lt=10, unit_price__lt=20) # or we can do as follows
    queryset7 = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)
    queryset8 = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20)) # this is OR lookup
    queryset9 = Product.objects.filter(Q(inventory__lt=10) & ~Q(unit_price__lt=20)) # this is AND NOT lookup

    # REFERENCING FIELDS USING F OBJECTS 
    queryset10 = Product.objects.filter(inventory=F('unit_price')) # this is equal to inventory = unit_price
    queryset11 = Product.objects.filter(inventory=F('collection__id')) # this is equal to inventory = collection.id, here collection is a foreign key field

    # SORTING
    queryset12 = Product.objects.order_by('title') # this is ascending order
    queryset13 = Product.objects.order_by('-title') # this is descending order
    queryset14 = Product.objects.order_by('unit_price', '-title').reverse() # this is ascending order by unit_price and descending order by title, reverse() is used to reverse the order
    queryset15 = Product.objects.filter(collection__id=1).order_by('unit_price') # this is ordering by unit_price for products in collection 1
    product1 = Product.objects.order_by('unit_price')[0]
    product2 = Product.objects.earliest('unit_price') # this is the cheapest product
    product3 = Product.objects.latest('unit_price') # this is the most expensive product

    # LIMITING PRODUCTS
    # queryset16 = Product.objects.all()[5:10]

    # SELECTING FIELDS TO QUERY
    queryset17 = Product.objects.values('id', 'title', 'collection__title') # this is selecting only id and title fields, collection__title is a foreign key field; it returns a dictionary not a product instance
    queryset18 = Product.objects.values_list('id', 'title', 'collection__title') # this is selecting only id and title fields, collection__title is a foreign key field; it returns a tuple not a product instance

    queryset19 = OrderItem.objects.values('product__id').distinct()
    queryset20 = Product.objects.filter(id__in = OrderItem.objects.values('product__id').distinct()).order_by('title')

    # DEFFERING FIELDS
    queryset21 = Product.objects.only('id', 'title') # values returns a dictionary, only returns the product instances
    queryset22 = Product.objects.defer('description') # defer returns a dictionary, defer returns the product instances but does not include the description field

    # SELECTING RELATED OBJECTS
    queryset23 = Product.objects.select_related('collection').all() # Uses SQL JOIN for ForeignKey/OneToOneField - fetches related objects in single query to avoid N+1
    queryset24 = Product.objects.prefetch_related('promotions').all() # Uses separate queries for ManyToManyField/reverse FK - fetches all related objects efficiently in 2 queries instead of N+1
    queryset25 = Product.objects.prefetch_related('promotions').select_related('collection').all() # prefetch_related and select_related can be used together to fetch related objects efficiently in 2 queries instead of N+1
    queryset26 = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5] # this is prefetching the products for each order

    # AGGREGATING OBJECTS
    result = Product.objects.filter(collection__id=1).aggregate(count = Count('id'), min_price = Min('unit_price'))

    # ANNOTATING OBJECTS
    queryset27 = Customer.objects.annotate(is_new=Value(True))
    queryset28 = Customer.objects.annotate(new_id=F('id') + 1)

    # CALLING DATABASE FUNCTIONS
    queryset29 = Customer.objects.annotate(
        full_name=Func(F('first_name'), Value(' '), F('last_name'), function='CONCAT')
    )
    queryset30 = Customer.objects.annotate(
        full_name = Concat('first_name', Value(' '), 'last_name')
    )

    # GROUPING Data
    queryset31 = Customer.objects.annotate(
        order_count = Count('order') # order_set isn't allowed by django for counting for reason unknown, here it allows order for reverse relationship
    )

    # WORKING WITH EXPRESSION WRAPPERS
        # Expression class is base class for all expressions
        # Its derivatives are: Value, F, Func, Aggregate (count, sum, avg, min, max) and ExpressionWrapper (to build complex expressions)
    discounted_price = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField()) # unit_price is decimal field and 0.8 is float, django won't allow it to multiply, so we use ExpressionWrapper to wrap the expression
    queryset32 = Product.objects.annotate(
        discounted_price = discounted_price
    )

    # QUERYING GENERIC RELATIONSHIPS
    content_type = ContentType.objects.get_for_model(Product)
    queryset33 = TaggedItem.objects \
    .select_related('tag') \
    .filter(
        content_type = content_type,
        object_id = 1
    )

    # CUSTOM MANAGERS
        # Custom managers are used to add custom methods to the model, a custom manager called TaggedItemManager is defined in tags/models.py
    queryset34 = TaggedItem.objects.get_tags_for(Product, 1)

    # UNDERSTANDING QUERYSET CACHE
    queryset35 = Product.objects.all()
    list(queryset35) # caching happends only if we evalate the entire query set first
    list(queryset35)
    queryset35[0]

    # CREATING OBJECTS
    # collection = Collection() # we didn't supply pk so django will create a new object
    # collection.title = 'Video Games'
    # # collection = Collection(title='Video Games') # we don't get intellisense this way and if we change name of this title field (by using rename symbol in vs code), it will not get updated automatically by vs code
    # # collection.featured_product = Product(pk=1) # by using pk we don't have to remember the name of the id
    # collection.featured_product_id = 1 # this is the same as the above, we can either use the product object or use the value of the primary key field; Django automatically creates the _id field for every ForeignKey, even though it's not in your model. collection.featured_product.id will also gives us id, but it will first fetch product object, while collection.featured_product_id will directly give us the id thats saved in the column without extra query; this is more efficient than above as it avoids the extra query to fetch the product object.
    # collection.save()
    # collection.id
    # # OR using create method
    # collection2 = Collection.objects.create(title='a', featured_product_id=1) # this is the same as the above, we can either use the product object or use the value of the primary key field; Django automatically creates the _id field for every ForeignKey, even though it's not in your model. collection.featured_product.id will also gives us id, but it will first fetch product object, while collection.featured_product_id will directly give us the id thats saved in the column without extra query; this is more efficient than above as it avoids the extra query to fetch the product object.
    # collection2.id

    # UPDATING OBJECTS
    # collection = Collection(pk=11)
    # collection.title = 'Games' # if we don't include this line, django will update title to '', thats why we should use other method of updating object
    # collection.featured_product = None
    # collection.save()
    # OR
    # collection = Collection.objects.get(pk=11) # read the object first to get values of all fields before updating
    # collection.featured_product = None
    # collection.save()
    # OR if we wanna save the query to read object first
    Collection.objects.filter(pk=11).update(featured_product=None) # this is the same as the above, we can either use the product object or use the value of the primary key field; Django automatically creates the _id field for every ForeignKey, even though it's not in your model. collection.featured_product.id will also gives us id, but it will first fetch product object, while collection.featured_product_id will directly give us the id thats saved in the column without extra query; this is more efficient than above as it avoids the extra query to fetch the product object.

    # DELETING OBJECTS
    # we can delete single object or multiple objects in a queryset
    # collection = Collection(pk=14)
    # collection.delete()
    # for multiple objects 
    # Collection.objects.filter(id__gt=5).delete() 

    # TRANSACTIONS (all changes should be saved in an atomic way, eg saving an order)
    # with transaction.atomic():
    #     order = Order()
    #     order.customer_id = 1
    #     order.save() # we should always create parent record first before we can create child records

    #     item = OrderItem()
    #     item.order = order
    #     item.product_id = -1
    #     item.quantity = 1
    #     item.unit_price = 10
    #     item.save()

    # EXECUTING RAW SQL QUERIES
    queryset36 = Product.objects.raw('SELECT id, title FROM store_product') # this queryset is differect from other querysets, we can't use filter, annotate and other methods
    # OR
    cursor = connection.cursor() # Direct database access, bypasses Django ORM, Returns raw tuples/dictionaries (not model instances) Full control over SQL Must manually handle connection/cursor lifecycle No automatic field mapping
    cursor.execute('SELECT id, title FROM store_product')
    cursor.close()
    # OR
    with connection.cursor() as cursor:
        cursor.execute('SELECT id, title FROM store_product')
    # OR
    # with connection.cursor() as cursor:
    #     cursor.callProc()




    return render(request, 'hello.html', {'name': 'Abhay', 'result': list(queryset36)})

