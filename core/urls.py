from django.views.generic import TemplateView
from django.urls import path

# URLConf
urlpatterns = [
    # path('hello/', views.say_hello)
    path('', TemplateView.as_view(template_name='core/index.html'))
]
