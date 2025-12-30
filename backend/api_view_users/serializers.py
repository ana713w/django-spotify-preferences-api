"""
Serializadores para la API de Spotify Preferences
"""

from rest_framework import serializers
from .models import User, MusicPreference


class UserSerializer(serializers.ModelSerializer):
    """Serializador para el modelo User"""
    
    preferences_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'full_name',
            'created_at',
            'updated_at',
            'preferences_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def get_preferences_count(self, obj):
        return obj.music_preferences.count()
    
    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "El username debe tener al menos 3 caracteres"
            )
        if len(value) > 100:
            raise serializers.ValidationError(
                "El username no puede tener más de 100 caracteres"
            )
        return value
    
    def validate_email(self, value):
        if self.instance is None:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "Este email ya está registrado"
                )
        else:
            if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(
                    "Este email ya está registrado"
                )
        return value.lower()


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear usuarios"""
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name']
    
    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "El username debe tener al menos 3 caracteres"
            )
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializador para actualizar usuarios"""
    class Meta:
        model = User
        fields = ['email', 'full_name']
        extra_kwargs = {
            'email': {'required': False},
            'full_name': {'required': False}
        }


class MusicPreferenceSerializer(serializers.ModelSerializer):
    """Serializador para el modelo MusicPreference"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = MusicPreference
        fields = [
            'id',
            'user',
            'user_username',
            'artist_name',
            'artist_id',
            'track_name',
            'track_id',
            'added_at'
        ]
        read_only_fields = ['id', 'added_at', 'user_username']
    
    def validate_user(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(
                f"Usuario con ID {value.id} no encontrado"
            )
        return value
    
    def validate_track_id(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError(
                "El track_id es obligatorio"
            )
        return value
    
    def validate(self, attrs):
        user = attrs.get('user')
        track_id = attrs.get('track_id')
        
        if self.instance is None:
            if MusicPreference.objects.filter(user=user, track_id=track_id).exists():
                raise serializers.ValidationError(
                    "Esta canción ya está en las preferencias del usuario"
                )
        
        return attrs


class MusicPreferenceCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear preferencias musicales"""
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = MusicPreference
        fields = [
            'user_id',
            'artist_name',
            'artist_id',
            'track_name',
            'track_id'
        ]
    
    def validate_user_id(self, value):
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                f"Usuario con ID {value} no encontrado"
            )
        return value
    
    def validate_track_id(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError(
                "El track_id es obligatorio"
            )
        if len(value) > 100:
            raise serializers.ValidationError(
                "El track_id no puede tener más de 100 caracteres"
            )
        return value

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        track_id = attrs.get('track_id')

        # Check if this preference already exists
        if MusicPreference.objects.filter(user_id=user_id, track_id=track_id).exists():
            raise serializers.ValidationError(
                "Esta canción ya está en las preferencias del usuario"
            )

        return attrs

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        validated_data['user'] = user
        return super().create(validated_data)