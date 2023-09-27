from django.contrib import admin
from django.urls import path

from foodplan import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('order/', views.order, name='order'),
    path('card/', views.card, name='card'),
]
