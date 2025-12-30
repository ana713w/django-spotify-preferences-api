"""
Modelos de la aplicación Spotify Preferences API
"""

from django.db import models
from django.core.validators import MinLengthValidator


class User(models.Model):
    """Modelo de Usuario"""
    username = models.CharField(
        max_length=150, 
        unique=True,
        validators=[MinLengthValidator(3)],
        help_text="Nombre de usuario único (mínimo 3 caracteres)"
    )
    email = models.EmailField(
        unique=True,
        help_text="Email del usuario"
    )
    full_name = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        help_text="Nombre completo del usuario (opcional)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del usuario"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "users"

    def __str__(self):
        return f"{self.username} ({self.email})"

    def get_preferences_count(self):
        return self.music_preferences.count()


class MusicPreference(models.Model):
    """Modelo de Preferencia Musical"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='music_preferences',
        help_text="Usuario propietario de esta preferencia"
    )
    artist_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Nombre del artista"
    )
    artist_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="ID del artista en Spotify"
    )
    track_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Nombre de la canción"
    )
    track_id = models.CharField(
        max_length=100,
        help_text="ID de la canción en Spotify (obligatorio)"
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha en que se agregó la preferencia"
    )

    class Meta:
        ordering = ['-added_at']
        verbose_name = "Music Preferences"
        verbose_name_plural = "Music Preferences"
        db_table = "music_preferences"
        unique_together = [['user', 'track_id']]

    def __str__(self):
        return f"{self.user.username} - {self.track_name or self.track_id}"