"""
URLs de la aplicación Spotify Preferences API
"""

from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Usuarios
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/preferences/', views.UserPreferencesView.as_view(), name='user-preferences'),
    
    # Preferencias Musicales
    path('music/preferences/', views.MusicPreferenceListCreateView.as_view(), name='preference-create'),
    path('music/preferences/<int:pk>/', views.MusicPreferenceDetailView.as_view(), name='preference-delete'),
    
    # Integración Spotify
    path('music/spotify/search/', views.SpotifySearchView.as_view(), name='spotify-search'),
    path('music/spotify/track/<str:track_id>/', views.SpotifyTrackDetailView.as_view(), name='spotify-track-detail'),
    path('music/spotify/artist/<str:artist_id>/', views.SpotifyArtistDetailView.as_view(), name='spotify-artist-detail'),
    path('music/spotify/artist/<str:artist_id>/top-tracks/', views.SpotifyArtistTopTracksView.as_view(), name='spotify-artist-top-tracks'),
]