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

    # Campos para el footer
    bio_footer = models.TextField(
        blank=True,
        help_text="Descripcion breve para el footer (primer parrafo)"
    )
    bio_footer_2 = models.TextField(
        blank=True,
        help_text="Descripcion adicional para el footer (segundo parrafo)"
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


class SeccionSuscripcion(models.Model):
    """Configuracion de la seccion de suscripcion (singleton)"""
    eyebrow = models.CharField(
        max_length=100,
        help_text="Texto superior pequeno, ej: Circulo Editorial Privado"
    )
    titulo = models.CharField(
        max_length=200,
        help_text="Titulo principal, ej: Boletin de Analisis Juridico y Politico"
    )
    descripcion = models.TextField(
        help_text="Texto descriptivo debajo del titulo"
    )
    nota = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nota al pie del formulario"
    )

    class Meta:
        verbose_name = 'Seccion de Suscripcion'
        verbose_name_plural = 'Seccion de Suscripcion'

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.pk and SeccionSuscripcion.objects.exists():
            raise ValidationError('Solo puede existir una seccion de suscripcion')
        super().save(*args, **kwargs)

    @classmethod
    def get_seccion(cls):
        return cls.objects.first()


class TickerItem(models.Model):
    """Elementos del ticker editorial superior"""
    texto = models.CharField(
        max_length=100,
        help_text="Ej: Estado de Derecho, Constitucionalismo"
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Menor numero aparece primero"
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Ticker'
        verbose_name_plural = 'Tickers'
        ordering = ['orden', 'pk']

    def __str__(self):
        return self.texto

    @classmethod
    def get_activos(cls):
        """Obtiene los elementos activos del ticker"""
        return cls.objects.filter(activo=True)


class Suscriptor(models.Model):
    """Suscriptores del sitio"""
    email = models.EmailField(unique=True)
    activo = models.BooleanField(
        default=False,
        help_text="Activar para permitir comentar"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Suscriptor'
        verbose_name_plural = 'Suscriptores'
        ordering = ['-fecha_registro']

    def __str__(self):
        return self.email

    @classmethod
    def get_by_email(cls, email):
        """Busca un suscriptor activo por email"""
        return cls.objects.filter(email=email, activo=True).first()


class Comentario(models.Model):
    """Comentarios de suscriptores en articulos"""
    articulo = models.ForeignKey(
        Articulo,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    suscriptor = models.ForeignKey(
        Suscriptor,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.suscriptor.email} en {self.articulo.titulo[:30]}'


class RedSocial(models.Model):
    """Redes sociales del autor para el footer"""

    ICONOS_CHOICES = [
        ('bi-twitter-x', 'X (Twitter)'),
        ('bi-linkedin', 'LinkedIn'),
        ('bi-youtube', 'YouTube'),
        ('bi-instagram', 'Instagram'),
        ('bi-facebook', 'Facebook'),
        ('bi-tiktok', 'TikTok'),
        ('bi-spotify', 'Spotify'),
        ('bi-envelope', 'Email'),
        ('bi-globe', 'Sitio Web'),
    ]

    nombre = models.CharField(
        max_length=100,
        help_text="Nombre visible de la red social, ej: YouTube / Podcast"
    )
    descripcion = models.CharField(
        max_length=200,
        help_text="Descripcion breve del contenido en esta red"
    )
    url = models.URLField(
        max_length=500,
        help_text="Enlace al perfil o canal"
    )
    icono = models.CharField(
        max_length=50,
        choices=ICONOS_CHOICES,
        help_text="Icono de Bootstrap Icons"
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Menor numero aparece primero"
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Red Social'
        verbose_name_plural = 'Redes Sociales'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

    @classmethod
    def get_activas(cls):
        """Obtiene las redes sociales activas ordenadas"""
        return cls.objects.filter(activo=True)
