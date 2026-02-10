from django.urls import path
from .views import home, articulo_detalle, suscribirse, agregar_comentario

urlpatterns = [
    path('', home, name='home'),
    path('suscribirse/', suscribirse, name='suscribirse'),
    path('articulo/<slug:slug>/', articulo_detalle, name='articulo_detalle'),
    path('articulo/<slug:slug>/comentar/', agregar_comentario, name='agregar_comentario'),
]
