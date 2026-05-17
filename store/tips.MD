# TIPS FOR PERFORMANCE OPTIMIZATION

## Preload related objects

Product.objects.select_related('...')
Product.objects.prefetch_related('...')

## Load only what you need

Product.objects.only('title')
Product.objects.defer('description')

## Use values

Product.objects.values()
Product.objects.values_list()

## Count properly

Product.objects.count()
lef(Produc.objects.all()) # bad

## Bulk create/update

Product.objects.bulk_create([])


## Optimizations

Optimize the python code

Re-write the query

Tune the database

Cache the result

Buy more hardware

Optimize the critical parts