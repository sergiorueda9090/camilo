from django.shortcuts import render, get_object_or_404
from .models import PerfilAutor, CapsulaJuridica, Articulo


def home(request):
    articulo_destacado = Articulo.get_destacado()

    # Excluir el destacado del archivo
    if articulo_destacado:
        articulos_archivo = Articulo.get_publicados().exclude(
            pk=articulo_destacado.pk
        )[:3]
    else:
        articulos_archivo = Articulo.get_publicados()[:3]

    context = {
        'perfil': PerfilAutor.get_perfil(),
        'capsulas': CapsulaJuridica.get_activas(),
        'articulo_destacado': articulo_destacado,
        'articulos_archivo': articulos_archivo,
    }
    return render(request, 'main/index.html', context)


def articulo_detalle(request, slug):
    articulo = get_object_or_404(Articulo, slug=slug, estado='publicado')
    articulo.incrementar_vistas()

    # Articulos relacionados (misma categoria)
    if articulo.categoria:
        relacionados = list(Articulo.get_publicados().filter(
            categoria=articulo.categoria
        ).exclude(pk=articulo.pk)[:3])
    else:
        relacionados = []

    # Si no hay suficientes, completar con otros
    if len(relacionados) < 3:
        ids_excluir = [articulo.pk] + [a.pk for a in relacionados]
        otros = list(Articulo.get_publicados().exclude(
            pk__in=ids_excluir
        )[:3 - len(relacionados)])
        relacionados = relacionados + otros

    # Navegacion anterior/siguiente
    articulo_anterior = Articulo.get_publicados().filter(
        fecha_publicacion__lt=articulo.fecha_publicacion
    ).first()

    articulo_siguiente = Articulo.get_publicados().filter(
        fecha_publicacion__gt=articulo.fecha_publicacion
    ).order_by('fecha_publicacion').first()

    context = {
        'perfil': PerfilAutor.get_perfil(),
        'capsulas': CapsulaJuridica.get_activas(),
        'articulo': articulo,
        'relacionados': relacionados,
        'articulo_anterior': articulo_anterior,
        'articulo_siguiente': articulo_siguiente,
    }
    return render(request, 'main/articulo-completo.html', context)
