from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.contrib.contenttypes.admin import GenericTabularInline
from django.urls import reverse
from django.utils.html import format_html, urlencode
from . import models
# Register your models here.

class InventoryFilter(admin.SimpleListFilter):
  title = 'inventory'
  parameter_name = 'inventory'

  def lookups(self, request, model_admin):
    return [
      ('<10', 'Low'),
    ]

  def queryset(self, request, queryset):
    if self.value() == '<10':
      return queryset.filter(inventory__lt=10)

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
  # fields = ['title', 'slug'] # this is used to display the fields in the admin change form
  # exclude = ['promotions'] # this is used to exclude the fields from the admin change form
  # readonly_fields = ['title'] # this is used to make a field read only
  prepopulated_fields = { # this is used to populate the slug field with the title field, it is a dictionary with the field to populate and the source field
    'slug': ['title'],
  }
  autocomplete_fields = ['collection']
  actions = ['clear_inventory']
  list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
  list_editable = ['unit_price']
  list_per_page = 10
  list_filter = ['collection', 'last_update', InventoryFilter]
  list_select_related = ['collection']
  search_fields = ['title']

  def collection_title(self, product):
    return product.collection.title

  @admin.display(ordering='inventory')
  def inventory_status(self, product):
    if product.inventory < 10:
      return 'Low'
    return 'OK'

  @admin.action(description='Clear inventory')
  def clear_inventory(self, request, queryset):
    updated_count = queryset.update(inventory=0)
    self.message_user(
      request,
      f'{updated_count} products were successfully updated.',
    )


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
  list_display = ['title', 'products_count']
  search_fields = ['title']
  
  @admin.display(ordering='products_count')
  def products_count(self, collection):
    url = (
      reverse('admin:store_product_changelist') # after adming there should be name of our app followed by model followed by the page
      + '?'
      + urlencode({
        'collection__id': str(collection.id)
      }))
    return format_html('<a href="{}">{}</a>', url, collection.products_count)

  def get_queryset(self, request):
    return super().get_queryset(request).annotate(
      products_count=Count('products')
    )

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
  list_display = ['first_name', 'last_name', 'membership']
  list_editable = ['membership']
  list_per_page = 10
  ordering = ['first_name', 'last_name']
  search_fields = ['first_name__istartswith', 'last_name__istartswith'] # __istartswith is a special filter that allows us to search for a string at the beginning of the field, i stands for case insensitive

class OrderItemInline(admin.TabularInline): # this inline classe indirectyly inherits from admin.ModelAdmin, so all the attributes also applies here like autocomplete_fields; Alternative to tabular inline is stacked inline
  autocomplete_fields = ['product']
  min_num = 1
  max_num = 10
  model = models.OrderItem
  extra = 0
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
  autocomplete_fields = ['customer']
  inlines = [OrderItemInline]
  list_display = ['id', 'placed_at', 'customer']

# admin.site.register(models.Product, ProductAdmin) # instead of this line we can just add the decorator above the class ProductAdmin

# google django model admin to learn more about how to customize the admin sitej