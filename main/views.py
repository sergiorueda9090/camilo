from django.shortcuts import render

def home(request):
    return render(request, 'main/index.html')

def articulo_completo(request):
    return render(request, 'main/articulo-completo.html')
