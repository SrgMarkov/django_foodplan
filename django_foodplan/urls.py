from django.contrib import admin
from django.urls import path

from foodplan import views

urlpatterns = [
    path('', views.show_index_page),
    path('admin/', admin.site.urls),
]
