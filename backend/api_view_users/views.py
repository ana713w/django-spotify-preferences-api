"""
Vistas de la API Spotify Preferences
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import User, MusicPreference
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    UserUpdateSerializer,
    MusicPreferenceSerializer,
    MusicPreferenceCreateSerializer
)
from .services import spotify_service


class UserListCreateView(APIView):
    """Vista para listar y crear usuarios"""
    
    def get(self, request):
        """Listar todos los usuarios"""
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error al obtener usuarios: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Crear un nuevo usuario"""
        serializer = UserCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            response_serializer = UserSerializer(user)
            return Response(
                {
                    "user_id": user.id,
                    "username": user.username,
                    "data": response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class UserDetailView(APIView):
    """Vista para operaciones individuales con usuarios"""
    
    def get(self, request, pk):
        """Obtener un usuario por ID"""
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        """Actualizar un usuario"""
        user = get_object_or_404(User, pk=pk)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "user_id": user.id,
                    "data": UserSerializer(user).data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request, pk):
        """Eliminar un usuario"""
        user = get_object_or_404(User, pk=pk)
        user_id = user.id
        username = user.username
        user.delete()
        
        return Response(
            {
                "user_id": user_id,
                "username": username
            },
            status=status.HTTP_200_OK
        )


class UserPreferencesView(APIView):
    """Vista para obtener las preferencias de un usuario"""
    
    def get(self, request, pk):
        """Obtener preferencias musicales de un usuario"""
        user = get_object_or_404(User, pk=pk)
        preferences = user.music_preferences.all()
        serializer = MusicPreferenceSerializer(preferences, many=True)
        
        return Response(
            {
                "user_id": user.id,
                "username": user.username,
                "preferences_count": preferences.count(),
                "preferences": serializer.data
            },
            status=status.HTTP_200_OK
        )


class MusicPreferenceListCreateView(APIView):
    """Vista para crear preferencias musicales"""
    
    def post(self, request):
        """Crear una nueva preferencia musical"""
        serializer = MusicPreferenceCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_id = serializer.validated_data.get('user_id')
        track_id = serializer.validated_data.get('track_id')
        track_name = serializer.validated_data.get('track_name')
        artist_name = serializer.validated_data.get('artist_name')
        artist_id = serializer.validated_data.get('artist_id')
        
        # Obtener información de Spotify si falta
        if not track_name or not artist_name or not artist_id:
            track_info = spotify_service.get_track_info(track_id)
            
            if "error" in track_info:
                return Response(
                    {
                        "details": track_info["error"]
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if not track_name:
                serializer.validated_data['track_name'] = track_info.get('name')
            if not artist_name:
                artists = track_info.get('artists', [])
                serializer.validated_data['artist_name'] = ", ".join(
                    [artist['name'] for artist in artists]
                )
            if not artist_id and track_info.get('artists'):
                serializer.validated_data['artist_id'] = track_info['artists'][0]['id']
        
        try:
            preference = serializer.save()
            response_serializer = MusicPreferenceSerializer(preference)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": f"Error al crear preferencia: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MusicPreferenceDetailView(APIView):
    """Vista para eliminar preferencias musicales"""
    
    def delete(self, request, pk):
        """Eliminar una preferencia musical"""
        preference = get_object_or_404(MusicPreference, pk=pk)
        preference_id = preference.id
        track_name = preference.track_name
        preference.delete()
        
        return Response(
            {
                "preference_id": preference_id,
                "track_name": track_name
            },
            status=status.HTTP_200_OK
        )


class SpotifySearchView(APIView):
    """Vista para buscar en Spotify"""
    
    def get(self, request):
        """Buscar en Spotify"""
        query = request.query_params.get('query')
        search_type = request.query_params.get('type', 'track')
        limit = int(request.query_params.get('limit', 10))
        
        if not query:
            return Response(
                {"error": "El parámetro 'query' es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if search_type not in ['track', 'artist', 'album']:
            return Response(
                {"error": "El tipo debe ser 'track', 'artist' o 'album'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if limit < 1 or limit > 50:
            return Response(
                {"error": "El límite debe estar entre 1 y 50"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = spotify_service.search(query, search_type, limit)
        
        if "error" in results:
            return Response(
                results,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(results, status=status.HTTP_200_OK)


class SpotifyTrackDetailView(APIView):
    """Vista para obtener información de una canción"""
    
    def get(self, request, track_id):
        """Obtener información de una canción de Spotify"""
        track_info = spotify_service.get_track_info(track_id)
        
        if "error" in track_info:
            return Response(
                track_info,
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(track_info, status=status.HTTP_200_OK)


class SpotifyArtistDetailView(APIView):
    """Vista para obtener información de un artista"""
    
    def get(self, request, artist_id):
        """Obtener información de un artista de Spotify"""
        artist_info = spotify_service.get_artist_info(artist_id)
        
        if "error" in artist_info:
            return Response(
                artist_info,
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(artist_info, status=status.HTTP_200_OK)


class SpotifyArtistTopTracksView(APIView):
    """Vista para obtener top tracks de un artista"""
    
    def get(self, request, artist_id):
        """Obtener top tracks de un artista"""
        country = request.query_params.get('country', 'US')
        
        if len(country) != 2:
            return Response(
                {"error": "El código de país debe tener 2 caracteres (ej: US, ES)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        top_tracks = spotify_service.get_artist_top_tracks(artist_id, country)
        
        if "error" in top_tracks:
            return Response(
                top_tracks,
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(top_tracks, status=status.HTTP_200_OK)