"""
Configuración del Panel de Administración
"""

from django.contrib import admin
from .models import User, MusicPreference


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuración del modelo User en el admin"""
    
    list_display = ['id', 'username', 'email', 'full_name', 'created_at', 'get_preferences_count']
    search_fields = ['username', 'email', 'full_name']
    list_filter = ['created_at', 'updated_at']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('username', 'email', 'full_name')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    list_per_page = 25
    
    def get_preferences_count(self, obj):
        return obj.music_preferences.count()
    get_preferences_count.short_description = 'Preferencias'


@admin.register(MusicPreference)
class MusicPreferenceAdmin(admin.ModelAdmin):
    """Configuración del modelo MusicPreference en el admin"""
    
    list_display = ['id', 'get_username', 'track_name', 'artist_name', 'track_id', 'added_at']
    search_fields = ['track_name', 'artist_name', 'track_id', 'user__username']
    list_filter = ['added_at', 'user']
    ordering = ['-added_at']
    readonly_fields = ['id', 'added_at']
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información de la Canción', {
            'fields': ('track_name', 'track_id', 'artist_name', 'artist_id')
        }),
        ('Metadata', {
            'fields': ('id', 'added_at'),
            'classes': ('collapse',),
        }),
    )
    
    list_per_page = 50
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Usuario'
    get_username.admin_order_field = 'user__username'


admin.site.site_header = 'Spotify Preferences API - Administración'
admin.site.site_title = 'Admin Panel'
admin.site.index_title = 'Panel de Control'