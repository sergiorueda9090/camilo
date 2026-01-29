from django.contrib import admin
from django.utils.html import format_html
from .models import PerfilAutor, CapsulaJuridica


@admin.register(PerfilAutor)
class PerfilAutorAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'firma', 'mostrar_foto']
    fieldsets = (
        ('Informacion basica', {
            'fields': ('titulo', 'nombre', 'descripcion', 'firma')
        }),
        ('Imagen', {
            'fields': ('foto',)
        }),
    )

    def mostrar_foto(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" width="40" height="40" '
                'style="border-radius:50%; object-fit:cover;" />',
                obj.foto.url
            )
        return '-'
    mostrar_foto.short_description = 'Foto'

    def has_add_permission(self, request):
        return not PerfilAutor.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CapsulaJuridica)
class CapsulaJuridicaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'orden', 'activo', 'contenido_corto']
    list_editable = ['orden', 'activo']
    list_filter = ['activo']
    search_fields = ['titulo', 'contenido']

    def contenido_corto(self, obj):
        if len(obj.contenido) > 80:
            return obj.contenido[:80] + '...'
        return obj.contenido
    contenido_corto.short_description = 'Contenido'

    def has_add_permission(self, request):
        # Solo permite agregar si hay menos de MAX_CAPSULAS
        return CapsulaJuridica.objects.count() < CapsulaJuridica.MAX_CAPSULAS

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        count = CapsulaJuridica.objects.count()
        extra_context['subtitle'] = f'{count}/{CapsulaJuridica.MAX_CAPSULAS} capsulas'
        return super().changelist_view(request, extra_context=extra_context)
