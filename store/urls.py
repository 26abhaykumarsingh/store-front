from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

# URLConf
urlpatterns = router.urls + products_router.urls 

# urlpatterns = [
#     # path('products/', views.product_list),
#     path('products/', views.ProductList.as_view()), # when as_view() is called it converts the class to regular function based view
#     path('products/<int:pk>/', views.ProductDetail.as_view()),
#     path('collections/', views.CollectionList.as_view()),
#     path('collections/<int:pk>/', views.CollectionDetail.as_view(), name='collection-detail')
# ]



# for building api there are 3 steps:
# 1. Create a serializer
# 2. Create a view
# 3. Register a route
