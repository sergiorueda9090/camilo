from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Categoria,
    Autor,
    Articulo,
    CitaDestacada,
    Comentario,
    CapsulaJuridica,
    ArchivoColumna,
    Suscriptor,
    ConfiguracionSitio,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'orden', 'total_articulos']
    list_editable = ['orden']
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ['nombre']

    def total_articulos(self, obj):
        return obj.articulos.count()
    total_articulos.short_description = 'Artículos'


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'cargo', 'es_principal', 'activo', 'mostrar_foto']
    list_filter = ['es_principal', 'activo']
    list_editable = ['es_principal', 'activo']
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ['nombre', 'cargo']
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'slug', 'titulo', 'cargo', 'foto', 'firma')
        }),
        ('Biografía', {
            'fields': ('biografia', 'biografia_corta')
        }),
        ('Redes sociales', {
            'fields': ('twitter', 'linkedin', 'youtube', 'instagram', 'email'),
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('es_principal', 'activo')
        }),
    )

    def mostrar_foto(self, obj):
        if obj.foto:
            return format_html('<img src="{}" width="40" height="40" style="border-radius:50%; object-fit:cover;" />', obj.foto.url)
        return '-'
    mostrar_foto.short_description = 'Foto'


class CitaDestacadaInline(admin.TabularInline):
    model = CitaDestacada
    extra = 1


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'categoria', 'estado', 'fecha_publicacion', 'vistas', 'destacado']
    list_filter = ['estado', 'categoria', 'autor', 'destacado', 'fecha_publicacion']
    list_editable = ['estado', 'destacado']
    search_fields = ['titulo', 'contenido', 'subtitulo']
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'fecha_publicacion'
    readonly_fields = ['vistas', 'fecha_creacion', 'fecha_actualizacion']
    inlines = [CitaDestacadaInline]

    fieldsets = (
        ('Contenido principal', {
            'fields': ('titulo', 'slug', 'subtitulo', 'contenido', 'extracto')
        }),
        ('Imagen', {
            'fields': ('imagen_destacada', 'imagen_url', 'pie_imagen')
        }),
        ('Clasificación', {
            'fields': ('autor', 'categoria')
        }),
        ('Publicación', {
            'fields': ('estado', 'destacado', 'fecha_publicacion')
        }),
        ('SEO', {
            'fields': ('meta_descripcion', 'meta_keywords', 'og_image'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('tiempo_lectura', 'vistas', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # Auto-calcular tiempo de lectura si no está definido
        if obj.contenido and obj.tiempo_lectura == 5:
            palabras = len(obj.contenido.split())
            obj.tiempo_lectura = max(1, palabras // 200)
        super().save_model(request, obj, form, change)


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'articulo_titulo', 'texto_corto', 'fecha_creacion', 'aprobado', 'es_autor', 'votos_utiles']
    list_filter = ['aprobado', 'es_autor', 'fecha_creacion']
    list_editable = ['aprobado', 'es_autor']
    search_fields = ['nombre', 'email', 'texto', 'articulo__titulo']
    readonly_fields = ['fecha_creacion', 'ip_address']
    raw_id_fields = ['articulo', 'padre']

    fieldsets = (
        ('Comentario', {
            'fields': ('articulo', 'padre', 'texto')
        }),
        ('Autor del comentario', {
            'fields': ('nombre', 'email', 'cargo')
        }),
        ('Moderación', {
            'fields': ('aprobado', 'es_autor', 'votos_utiles')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'ip_address'),
            'classes': ('collapse',)
        }),
    )

    def articulo_titulo(self, obj):
        return obj.articulo.titulo[:40] + '...' if len(obj.articulo.titulo) > 40 else obj.articulo.titulo
    articulo_titulo.short_description = 'Artículo'

    def texto_corto(self, obj):
        return obj.texto[:60] + '...' if len(obj.texto) > 60 else obj.texto
    texto_corto.short_description = 'Comentario'

    actions = ['aprobar_comentarios', 'rechazar_comentarios']

    def aprobar_comentarios(self, request, queryset):
        queryset.update(aprobado=True)
        self.message_user(request, f'{queryset.count()} comentarios aprobados.')
    aprobar_comentarios.short_description = 'Aprobar comentarios seleccionados'

    def rechazar_comentarios(self, request, queryset):
        queryset.update(aprobado=False)
        self.message_user(request, f'{queryset.count()} comentarios rechazados.')
    rechazar_comentarios.short_description = 'Rechazar comentarios seleccionados'


@admin.register(CapsulaJuridica)
class CapsulaJuridicaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'contenido_corto', 'activo', 'orden', 'fecha_creacion']
    list_filter = ['activo']
    list_editable = ['activo', 'orden']
    search_fields = ['titulo', 'contenido']

    def contenido_corto(self, obj):
        return obj.contenido[:80] + '...' if len(obj.contenido) > 80 else obj.contenido
    contenido_corto.short_description = 'Contenido'


@admin.register(ArchivoColumna)
class ArchivoColumnaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha', 'tiene_url']
    list_filter = ['fecha']
    search_fields = ['titulo', 'descripcion']
    date_hierarchy = 'fecha'

    def tiene_url(self, obj):
        return bool(obj.url)
    tiene_url.boolean = True
    tiene_url.short_description = 'URL'


@admin.register(Suscriptor)
class SuscriptorAdmin(admin.ModelAdmin):
    list_display = ['email', 'nombre', 'fecha_suscripcion', 'activo', 'confirmado']
    list_filter = ['activo', 'confirmado', 'fecha_suscripcion']
    list_editable = ['activo']
    search_fields = ['email', 'nombre']
    date_hierarchy = 'fecha_suscripcion'
    readonly_fields = ['fecha_suscripcion', 'token_confirmacion']

    actions = ['activar_suscriptores', 'desactivar_suscriptores']

    def activar_suscriptores(self, request, queryset):
        queryset.update(activo=True)
        self.message_user(request, f'{queryset.count()} suscriptores activados.')
    activar_suscriptores.short_description = 'Activar suscriptores seleccionados'

    def desactivar_suscriptores(self, request, queryset):
        queryset.update(activo=False)
        self.message_user(request, f'{queryset.count()} suscriptores desactivados.')
    desactivar_suscriptores.short_description = 'Desactivar suscriptores seleccionados'


@admin.register(ConfiguracionSitio)
class ConfiguracionSitioAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Información del sitio', {
            'fields': ('nombre_sitio', 'subtitulo', 'descripcion', 'ticker_texto')
        }),
        ('Contacto', {
            'fields': ('email_contacto', 'ubicacion')
        }),
        ('Redes sociales', {
            'fields': ('twitter', 'linkedin', 'youtube', 'instagram')
        }),
    )

    def has_add_permission(self, request):
        # Solo permitir una instancia
        return not ConfiguracionSitio.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# Personalizar el admin site
admin.site.site_header = 'Camilo Soler Rueda - Administración'
admin.site.site_title = 'Admin CSR'
admin.site.index_title = 'Panel de Administración'
