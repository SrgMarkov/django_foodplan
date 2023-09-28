from django.contrib import admin
from django.urls import path

from foodplan.views import *


urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('order/', order, name='order'),
    path('card/', card, name='card'),
    path('auth/', LoginUser.as_view(), name='auth'),
    path('registration/', RegisterUser.as_view(), name='registration'),
    path('logout/', logout_user, name='logout'),
    path('lk/', lk, name='lk'),
]
