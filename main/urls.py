from django.urls import path
from .views import home, articulo_detalle

urlpatterns = [
    path('', home, name='home'),
    path('articulo/<slug:slug>/', articulo_detalle, name='articulo_detalle'),
]
