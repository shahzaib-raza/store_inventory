from . import views
from django.urls import path

urlpatterns = [
    path("", views.index),
    path("index/", views.index),
    path("login/", views.login),
    path('stock/', views.stock),
    path('inv_in/', views.inv_in),
    path('inv_out/', views.inv_out),
]