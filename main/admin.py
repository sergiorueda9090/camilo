from django.contrib import admin
from django.utils.html import format_html
from .models import PerfilAutor, CapsulaJuridica, Categoria, Articulo, RedSocial


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
        ('Footer', {
            'fields': ('bio_footer', 'bio_footer_2'),
            'description': 'Textos que aparecen en la seccion "Sobre el autor" del footer'
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
        return CapsulaJuridica.objects.count() < CapsulaJuridica.MAX_CAPSULAS

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        count = CapsulaJuridica.objects.count()
        extra_context['subtitle'] = f'{count}/{CapsulaJuridica.MAX_CAPSULAS} capsulas'
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'total_articulos']
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ['nombre']

    def total_articulos(self, obj):
        return obj.articulos.count()
    total_articulos.short_description = 'Articulos'


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'categoria', 'estado', 'destacado',
        'fecha_publicacion', 'vistas'
    ]
    list_filter = ['estado', 'categoria', 'destacado', 'fecha_publicacion']
    list_editable = ['estado', 'destacado']
    search_fields = ['titulo', 'contenido', 'subtitulo', 'extracto']
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'fecha_publicacion'
    readonly_fields = ['vistas', 'fecha_creacion', 'fecha_actualizacion', 'tiempo_lectura']

    fieldsets = (
        ('Contenido principal', {
            'fields': ('titulo', 'slug', 'subtitulo', 'extracto', 'contenido')
        }),
        ('Imagen', {
            'fields': ('imagen_destacada', 'imagen_url', 'pie_imagen')
        }),
        ('Clasificacion', {
            'fields': ('autor', 'categoria')
        }),
        ('Publicacion', {
            'fields': ('estado', 'destacado', 'fecha_publicacion')
        }),
        ('SEO', {
            'fields': ('meta_descripcion', 'meta_keywords', 'og_image'),
            'classes': ('collapse',)
        }),
        ('Estadisticas', {
            'fields': ('tiempo_lectura', 'vistas', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RedSocial)
class RedSocialAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono_preview', 'descripcion_corta', 'orden', 'activo']
    list_editable = ['orden', 'activo']
    list_filter = ['activo', 'icono']
    search_fields = ['nombre', 'descripcion']

    def icono_preview(self, obj):
        return format_html('<i class="bi {}"></i> {}', obj.icono, obj.get_icono_display())
    icono_preview.short_description = 'Icono'

    def descripcion_corta(self, obj):
        if len(obj.descripcion) > 50:
            return obj.descripcion[:50] + '...'
        return obj.descripcion
    descripcion_corta.short_description = 'Descripcion'
