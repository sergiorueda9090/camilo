from django.shortcuts import render
from .models import PerfilAutor, CapsulaJuridica


def home(request):
    context = {
        'perfil': PerfilAutor.get_perfil(),
        'capsulas': CapsulaJuridica.get_activas(),
    }
    return render(request, 'main/index.html', context)


def articulo_completo(request):
    context = {
        'perfil': PerfilAutor.get_perfil(),
        'capsulas': CapsulaJuridica.get_activas(),
    }
    return render(request, 'main/articulo-completo.html', context)
