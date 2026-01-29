from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from ckeditor.fields import RichTextField


class PerfilAutor(models.Model):
    """Perfil del autor principal del sitio (singleton)"""
    titulo = models.CharField(
        max_length=180,
        blank=True,
        help_text="Ej: Dr., Dra., Mag., Abg."
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(
        help_text="Descripcion breve para mostrar en el sidebar"
    )
    firma = models.CharField(
        max_length=100,
        blank=True,
        help_text="Firma estilizada, ej: Camilo Soler R."
    )
    foto = models.ImageField(
        upload_to='autor/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Perfil del Autor'
        verbose_name_plural = 'Perfil del Autor'

    def __str__(self):
        if self.titulo:
            return f"{self.titulo} {self.nombre}"
        return self.nombre

    def save(self, *args, **kwargs):
        # Solo permite un registro
        if not self.pk and PerfilAutor.objects.exists():
            raise ValidationError('Solo puede existir un perfil de autor')
        super().save(*args, **kwargs)

    def nombre_completo(self):
        """Retorna el nombre con titulo"""
        if self.titulo:
            return f"{self.titulo} {self.nombre}"
        return self.nombre

    @classmethod
    def get_perfil(cls):
        """Obtiene el perfil del autor (singleton)"""
        return cls.objects.first()


class CapsulaJuridica(models.Model):
    """Capsulas juridicas breves para el sidebar (maximo 5)"""
    MAX_CAPSULAS = 5

    titulo = models.CharField(max_length=200)
    contenido = models.TextField(
        max_length=500,
        help_text="Contenido breve de la capsula"
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Menor numero aparece primero"
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Capsula Juridica'
        verbose_name_plural = 'Capsulas Juridicas'
        ordering = ['orden', '-pk']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        # Limitar a MAX_CAPSULAS registros
        if not self.pk and CapsulaJuridica.objects.count() >= self.MAX_CAPSULAS:
            raise ValidationError(
                f'Solo se permiten {self.MAX_CAPSULAS} capsulas juridicas'
            )
        super().save(*args, **kwargs)

    @classmethod
    def get_activas(cls):
        """Obtiene las capsulas activas ordenadas"""
        return cls.objects.filter(activo=True)


class Categoria(models.Model):
    """Categorias para organizar los articulos"""
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Articulo(models.Model):
    """Articulos y columnas del sitio"""

    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('publicado', 'Publicado'),
    ]

    # Informacion basica
    titulo = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    subtitulo = models.CharField(
        max_length=500,
        blank=True,
        help_text="Lead o bajada del articulo"
    )

    # Contenido
    contenido = RichTextField()
    extracto = models.TextField(
        max_length=500,
        blank=True,
        help_text="Resumen breve para listados y SEO"
    )

    # Imagen
    imagen_destacada = models.ImageField(
        upload_to='articulos/',
        blank=True,
        null=True
    )
    imagen_url = models.URLField(
        max_length=200,
        blank=True,
        help_text="URL externa de imagen (alternativa a subir archivo)"
    )
    pie_imagen = models.CharField(
        max_length=200,
        blank=True,
        help_text="Descripcion o creditos de la imagen"
    )

    # SEO
    meta_descripcion = models.CharField(
        max_length=160,
        blank=True,
        help_text="Descripcion para motores de busqueda"
    )
    meta_keywords = models.CharField(
        max_length=200,
        blank=True,
        help_text="Palabras clave separadas por coma"
    )
    og_image = models.URLField(
        max_length=200,
        blank=True,
        help_text="URL de imagen para redes sociales"
    )

    # Relaciones
    autor = models.ForeignKey(
        PerfilAutor,
        on_delete=models.CASCADE,
        related_name='articulos'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articulos'
    )

    # Metadata
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    tiempo_lectura = models.PositiveIntegerField(
        default=5,
        help_text="Minutos estimados de lectura"
    )
    vistas = models.PositiveIntegerField(default=0)

    # Estado
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='borrador'
    )
    destacado = models.BooleanField(
        default=False,
        help_text="Mostrar en la pagina principal"
    )

    class Meta:
        verbose_name = 'Articulo'
        verbose_name_plural = 'Articulos'
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        # Calcular tiempo de lectura (200 palabras por minuto)
        if self.contenido:
            palabras = len(self.contenido.split())
            self.tiempo_lectura = max(1, palabras // 200)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('articulo_detalle', kwargs={'slug': self.slug})

    def incrementar_vistas(self):
        self.vistas += 1
        self.save(update_fields=['vistas'])

    @classmethod
    def get_publicados(cls):
        """Obtiene articulos publicados"""
        return cls.objects.filter(estado='publicado')

    @classmethod
    def get_destacado(cls):
        """Obtiene el articulo destacado o el mas reciente"""
        destacado = cls.objects.filter(
            estado='publicado',
            destacado=True
        ).first()
        if not destacado:
            destacado = cls.objects.filter(estado='publicado').first()
        return destacado
