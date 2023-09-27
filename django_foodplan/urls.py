from django.contrib import admin
from django.urls import path

from foodplan.views import *


urlpatterns = [
    path('', index, name='index'),
    path('free_recipes/', free_recipes, name='free_recipes'),
    path('admin/', admin.site.urls),
    path('order/', order, name='order'),
    path('card/', card, name='card'),
    path('auth/', auth, name='auth'),
    path('registration/', RegisterUser.as_view(), name='registration'),
    path('lk/', lk, name='lk'),
]
