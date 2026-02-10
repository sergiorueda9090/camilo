from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import PerfilAutor, CapsulaJuridica, Articulo, SeccionSuscripcion, TickerItem, RedSocial, Suscriptor, Comentario


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
        'ticker_items': TickerItem.get_activos(),
        'suscripcion': SeccionSuscripcion.get_seccion(),
        'redes_sociales': RedSocial.get_activas(),
        'articulos_footer': Articulo.get_publicados()[:4],
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

    # Obtener y limpiar mensajes de error de comentarios
    comentario_error = request.session.pop('comentario_error', '')
    comentario_email = request.session.pop('comentario_email', '')
    comentario_texto = request.session.pop('comentario_texto', '')

    context = {
        'perfil': PerfilAutor.get_perfil(),
        'capsulas': CapsulaJuridica.get_activas(),
        'ticker_items': TickerItem.get_activos(),
        'suscripcion': SeccionSuscripcion.get_seccion(),
        'redes_sociales': RedSocial.get_activas(),
        'articulos_footer': Articulo.get_publicados()[:4],
        'articulo': articulo,
        'comentarios': articulo.comentarios.select_related('suscriptor').all(),
        'comentario_error': comentario_error,
        'comentario_email': comentario_email,
        'comentario_texto': comentario_texto,
        'relacionados': relacionados,
        'articulo_anterior': articulo_anterior,
        'articulo_siguiente': articulo_siguiente,
    }
    return render(request, 'main/articulo-completo.html', context)


@require_POST
def suscribirse(request):
    email = request.POST.get('email', '').strip()
    if not email:
        return JsonResponse({'ok': False, 'mensaje': 'Ingrese un correo valido.'}, status=400)

    suscriptor, created = Suscriptor.objects.get_or_create(email=email)
    if created:
        mensaje = 'Solicitud recibida. Un administrador revisara su registro.'
    else:
        mensaje = 'Este correo ya esta registrado.'

    return JsonResponse({'ok': True, 'mensaje': mensaje})


@require_POST
def agregar_comentario(request, slug):
    articulo = get_object_or_404(Articulo, slug=slug, estado='publicado')
    email = request.POST.get('email', '').strip()
    texto = request.POST.get('texto', '').strip()

    if not email or not texto:
        return redirect('articulo_detalle', slug=slug)

    suscriptor = Suscriptor.get_by_email(email)
    if not suscriptor:
        # Store error in session for display
        request.session['comentario_error'] = 'Su correo no esta registrado o no ha sido aprobado aun.'
        request.session['comentario_email'] = email
        request.session['comentario_texto'] = texto
        return redirect('articulo_detalle', slug=slug)

    Comentario.objects.create(
        articulo=articulo,
        suscriptor=suscriptor,
        texto=texto,
    )
    return redirect('articulo_detalle', slug=slug)
