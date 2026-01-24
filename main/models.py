from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Categoria(models.Model):
    """Categorías para organizar los artículos"""
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('categoria_detalle', kwargs={'slug': self.slug})


class Autor(models.Model):
    """Información del autor de los artículos"""
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    titulo = models.CharField(max_length=100, blank=True, help_text="Ej: Dr., Dra., Mag.")
    cargo = models.CharField(max_length=200, blank=True, help_text="Ej: Abogado constitucionalista")
    biografia = models.TextField(blank=True)
    biografia_corta = models.CharField(max_length=300, blank=True, help_text="Descripción breve para sidebar")
    foto = models.ImageField(upload_to='autores/', blank=True, null=True)
    firma = models.CharField(max_length=100, blank=True, help_text="Firma estilizada, ej: Camilo Soler R.")

    # Redes sociales
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    email = models.EmailField(blank=True)

    es_principal = models.BooleanField(default=False, help_text="Autor principal del sitio")
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Autor'
        verbose_name_plural = 'Autores'
        ordering = ['-es_principal', 'nombre']

    def __str__(self):
        if self.titulo:
            return f"{self.titulo} {self.nombre}"
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def nombre_completo(self):
        if self.titulo:
            return f"{self.titulo} {self.nombre}"
        return self.nombre


class Articulo(models.Model):
    """Artículos, columnas y análisis"""

    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('revision', 'En revisión'),
        ('publicado', 'Publicado'),
    ]

    # Información básica
    titulo = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    subtitulo = models.CharField(max_length=500, blank=True, help_text="Lead o bajada del artículo")

    # Contenido
    contenido = models.TextField()
    extracto = models.TextField(max_length=500, blank=True, help_text="Resumen para listados y SEO")

    # Imagen
    imagen_destacada = models.ImageField(upload_to='articulos/', blank=True, null=True)
    imagen_url = models.URLField(blank=True, help_text="URL externa de imagen (alternativa)")
    pie_imagen = models.CharField(max_length=200, blank=True)

    # Relaciones
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='articulos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='articulos')

    # Metadata
    fecha_publicacion = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    tiempo_lectura = models.PositiveIntegerField(default=5, help_text="Minutos estimados de lectura")
    vistas = models.PositiveIntegerField(default=0)

    # Estado
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    destacado = models.BooleanField(default=False, help_text="Mostrar en posición destacada")

    # SEO
    meta_descripcion = models.CharField(max_length=160, blank=True, help_text="Descripción para SEO")
    meta_keywords = models.CharField(max_length=200, blank=True, help_text="Palabras clave separadas por coma")
    og_image = models.URLField(blank=True, help_text="Imagen para compartir en redes sociales")

    class Meta:
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'
        ordering = ['-fecha_publicacion', '-fecha_creacion']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        # Calcular tiempo de lectura aproximado (200 palabras por minuto)
        if self.contenido and not self.tiempo_lectura:
            palabras = len(self.contenido.split())
            self.tiempo_lectura = max(1, palabras // 200)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('articulo_detalle', kwargs={'slug': self.slug})

    def incrementar_vistas(self):
        self.vistas += 1
        self.save(update_fields=['vistas'])

    def get_imagen(self):
        """Retorna la imagen destacada o la URL externa"""
        if self.imagen_destacada:
            return self.imagen_destacada.url
        return self.imagen_url or ''


class CitaDestacada(models.Model):
    """Citas destacadas (pullquotes) dentro de un artículo"""
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='citas')
    texto = models.TextField()
    autor_cita = models.CharField(max_length=200, blank=True, help_text="Autor de la cita si no es el autor del artículo")
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Cita destacada'
        verbose_name_plural = 'Citas destacadas'
        ordering = ['orden']

    def __str__(self):
        return f"{self.texto[:50]}..."


class Comentario(models.Model):
    """Comentarios en los artículos"""
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='comentarios')
    padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='respuestas')

    # Datos del comentarista
    nombre = models.CharField(max_length=200)
    email = models.EmailField()
    cargo = models.CharField(max_length=200, blank=True, help_text="Cargo / Institución")

    # Contenido
    texto = models.TextField()

    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    votos_utiles = models.PositiveIntegerField(default=0)

    # Moderación
    aprobado = models.BooleanField(default=False)
    es_autor = models.BooleanField(default=False, help_text="Comentario del autor del artículo")

    # Para evitar spam
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} en {self.articulo.titulo[:30]}"

    def es_respuesta(self):
        return self.padre is not None


class CapsulaJuridica(models.Model):
    """Cápsulas jurídicas breves para el sidebar"""
    titulo = models.CharField(max_length=200)
    contenido = models.TextField(max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Cápsula jurídica'
        verbose_name_plural = 'Cápsulas jurídicas'
        ordering = ['orden', '-fecha_creacion']

    def __str__(self):
        return self.titulo


class ArchivoColumna(models.Model):
    """Archivo de columnas antiguas (enlaces externos)"""
    titulo = models.CharField(max_length=300)
    url = models.URLField(blank=True)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = 'Archivo de columna'
        verbose_name_plural = 'Archivo de columnas'
        ordering = ['-fecha']

    def __str__(self):
        return self.titulo


class Suscriptor(models.Model):
    """Suscriptores al newsletter"""
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=200, blank=True)
    fecha_suscripcion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    confirmado = models.BooleanField(default=False)
    token_confirmacion = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Suscriptor'
        verbose_name_plural = 'Suscriptores'
        ordering = ['-fecha_suscripcion']

    def __str__(self):
        return self.email


class ConfiguracionSitio(models.Model):
    """Configuración general del sitio (singleton)"""
    nombre_sitio = models.CharField(max_length=200, default="Camilo Andres Soler Rueda")
    subtitulo = models.CharField(max_length=300, default="Derecho - Politica - Pensamiento Critico")
    descripcion = models.TextField(blank=True)

    # Ticker
    ticker_texto = models.CharField(
        max_length=500,
        default="Estado de Derecho * Constitucionalismo * Analisis Politico * Opinion Juridica"
    )

    # Contacto
    email_contacto = models.EmailField(blank=True)
    ubicacion = models.CharField(max_length=200, blank=True, default="Bogota, Colombia")

    # Redes sociales
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    instagram = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Configuración del sitio'
        verbose_name_plural = 'Configuración del sitio'

    def __str__(self):
        return self.nombre_sitio

    def save(self, *args, **kwargs):
        # Asegurar que solo exista una instancia
        if not self.pk and ConfiguracionSitio.objects.exists():
            raise ValueError('Solo puede existir una configuración del sitio')
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        """Obtener o crear la configuración del sitio"""
        config, created = cls.objects.get_or_create(pk=1)
        return config
