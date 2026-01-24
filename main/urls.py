from django.urls import path
from .views import home, articulo_completo

urlpatterns = [
    path('', home, name='home'),
    path('articulo/', articulo_completo, name='articulo_completo'),
]
