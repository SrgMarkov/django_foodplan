from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from foodplan.views import *


urlpatterns = [
    path('', index, name='index'),
    path('free_recipes/', free_recipes, name='free_recipes'),
    path('admin/', admin.site.urls),
    path('order/', order, name='order'),
    path('pay/', pay, name='pay'),
    path('process_payment/', process_payment, name='process_payment'),
    path('card/', card, name='card'),
    path('auth/', LoginUser.as_view(), name='auth'),
    path('registration/', RegisterUser.as_view(), name='registration'),
    path('logout/', logout_user, name='logout'),
    path('lk/', lk, name='lk'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
