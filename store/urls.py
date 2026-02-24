from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)

# URLConf
urlpatterns = router.urls

# urlpatterns = [
#     # path('products/', views.product_list),
#     path('products/', views.ProductList.as_view()), # when as_view() is called it converts the class to regular function based view
#     path('products/<int:pk>/', views.ProductDetail.as_view()),
#     path('collections/', views.CollectionList.as_view()),
#     path('collections/<int:pk>/', views.CollectionDetail.as_view(), name='collection-detail')
# ]
