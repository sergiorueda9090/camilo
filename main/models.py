from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


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
