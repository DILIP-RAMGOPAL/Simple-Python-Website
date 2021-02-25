from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage),
    path('cidr', views.cidr),
    path('timezone', views.convert_timezone),
    path('epoch', views.epoch),
    path('disclaimer', views.disclaimer),
]
