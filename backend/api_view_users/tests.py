from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User, MusicPreference
from unittest.mock import patch, MagicMock


class UserModelTest(TestCase):
    """Tests for User model"""
    
    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
            email="test@example.com",
            full_name="Test User"
        )
    
    def test_user_creation(self):
        """Test user is created correctly"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.full_name, "Test User")
        self.assertIsNotNone(self.user.created_at)
        self.assertIsNotNone(self.user.updated_at)
    
    def test_user_str_method(self):
        """Test user string representation"""
        expected = f"{self.user.username} ({self.user.email})"
        self.assertEqual(str(self.user), expected)
    
    def test_username_unique(self):
        """Test username must be unique"""
        with self.assertRaises(Exception):
            User.objects.create(
                username="testuser",
                email="another@example.com"
            )
    
    def test_email_unique(self):
        """Test email must be unique"""
        with self.assertRaises(Exception):
            User.objects.create(
                username="anotheruser",
                email="test@example.com"
            )


class MusicPreferenceModelTest(TestCase):
    """Tests for MusicPreference model"""
    
    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
            email="test@example.com"
        )
        self.preference = MusicPreference.objects.create(
            user=self.user,
            track_id="3z8h0TU7ReDPLIbEnYhWZb",
            track_name="Bohemian Rhapsody",
            artist_name="Queen",
            artist_id="1dfeR4HaWDbWqFHLkxsg1d"
        )
    
    def test_preference_creation(self):
        """Test music preference is created correctly"""
        self.assertEqual(self.preference.user, self.user)
        self.assertEqual(self.preference.track_id, "3z8h0TU7ReDPLIbEnYhWZb")
        self.assertEqual(self.preference.track_name, "Bohemian Rhapsody")
        self.assertIsNotNone(self.preference.added_at)
    
    def test_preference_str_method(self):
        """Test preference string representation"""
        expected = f"{self.user.username} - {self.preference.track_name}"
        self.assertEqual(str(self.preference), expected)
    
    def test_user_cascade_delete(self):
        """Test preferences are deleted when user is deleted"""
        user_id = self.user.id
        self.user.delete()
        
        preferences = MusicPreference.objects.filter(user_id=user_id)
        self.assertEqual(preferences.count(), 0)


class UserAPITest(APITestCase):
    """Tests for User API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "full_name": "John Doe"
        }
        self.user = User.objects.create(**self.user_data)
    
    def test_create_user(self):
        """Test creating a new user via API"""
        url = reverse('api:user-list-create')
        data = {
            "username": "janedoe",
            "email": "jane@example.com",
            "full_name": "Jane Doe"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data['username'], 'janedoe')
    
    def test_create_user_invalid_username(self):
        """Test creating user with short username fails"""
        url = reverse('api:user-list-create')
        data = {
            "username": "ab",  # Too short
            "email": "test@example.com"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_user_duplicate_email(self):
        """Test creating user with duplicate email fails"""
        url = reverse('api:user-list-create')
        data = {
            "username": "newuser",
            "email": "john@example.com"  # Already exists
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_users(self):
        """Test listing all users"""
        url = reverse('api:user-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_user_detail(self):
        """Test getting user by ID"""
        url = reverse('api:user-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
    
    def test_get_user_not_found(self):
        """Test getting non-existent user returns 404"""
        url = reverse('api:user-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_user(self):
        """Test updating user"""
        url = reverse('api:user-detail', kwargs={'pk': self.user.id})
        data = {
            "email": "newemail@example.com",
            "full_name": "John Updated"
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@example.com")
        self.assertEqual(self.user.full_name, "John Updated")
    
    def test_delete_user(self):
        """Test deleting user"""
        url = reverse('api:user-detail', kwargs={'pk': self.user.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 0)


class MusicPreferenceAPITest(APITestCase):
    """Tests for Music Preference API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="testuser",
            email="test@example.com"
        )
        
        # Mock Spotify service response
        self.mock_track_info = {
            "id": "3z8h0TU7ReDPLIbEnYhWZb",
            "name": "Bohemian Rhapsody",
            "artists": [
                {
                    "id": "1dfeR4HaWDbWqFHLkxsg1d",
                    "name": "Queen"
                }
            ]
        }
    
    @patch('api_view_users.views.spotify_service.get_track_info')
    def test_create_preference_with_spotify_lookup(self, mock_spotify):
        """Test creating preference with Spotify API lookup"""
        mock_spotify.return_value = self.mock_track_info
        
        url = reverse('api:preference-create')
        data = {
            "user_id": self.user.id,
            "track_id": "3z8h0TU7ReDPLIbEnYhWZb"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MusicPreference.objects.count(), 1)
        self.assertEqual(response.data['track_name'], 'Bohemian Rhapsody')
        self.assertEqual(response.data['artist_name'], 'Queen')
        mock_spotify.assert_called_once_with("3z8h0TU7ReDPLIbEnYhWZb")
    
    def test_create_preference_with_full_data(self):
        """Test creating preference with all data provided"""
        url = reverse('api:preference-create')
        data = {
            "user_id": self.user.id,
            "track_id": "3z8h0TU7ReDPLIbEnYhWZb",
            "track_name": "Bohemian Rhapsody",
            "artist_name": "Queen",
            "artist_id": "1dfeR4HaWDbWqFHLkxsg1d"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['track_name'], 'Bohemian Rhapsody')
    
    def test_create_preference_user_not_found(self):
        """Test creating preference with non-existent user fails"""
        url = reverse('api:preference-create')
        data = {
            "user_id": 9999,
            "track_id": "3z8h0TU7ReDPLIbEnYhWZb"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_preference(self):
        """Test deleting a preference"""
        preference = MusicPreference.objects.create(
            user=self.user,
            track_id="3z8h0TU7ReDPLIbEnYhWZb",
            track_name="Bohemian Rhapsody"
        )
        
        url = reverse('api:preference-delete', kwargs={'pk': preference.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MusicPreference.objects.count(), 0)
    
    def test_get_user_preferences(self):
        """Test getting all preferences of a user"""
        MusicPreference.objects.create(
            user=self.user,
            track_id="track1",
            track_name="Song 1"
        )
        MusicPreference.objects.create(
            user=self.user,
            track_id="track2",
            track_name="Song 2"
        )
        
        url = reverse('api:user-preferences', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['preferences_count'], 2)
        self.assertEqual(len(response.data['preferences']), 2)


class SpotifyIntegrationAPITest(APITestCase):
    """Tests for Spotify Integration API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
    
    @patch('api_view_users.views.spotify_service.search')
    def test_search_spotify(self, mock_search):
        """Test searching on Spotify"""
        mock_search.return_value = {
            "tracks": {
                "items": [
                    {"id": "123", "name": "Test Song"}
                ]
            }
        }
        
        url = reverse('api:spotify-search')
        response = self.client.get(url, {
            'query': 'test',
            'type': 'track',
            'limit': 5
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_search.assert_called_once_with('test', 'track', 5)
    
    def test_search_spotify_missing_query(self):
        """Test search without query parameter fails"""
        url = reverse('api:spotify-search')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_spotify_invalid_type(self):
        """Test search with invalid type fails"""
        url = reverse('api:spotify-search')
        response = self.client.get(url, {
            'query': 'test',
            'type': 'invalid'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_spotify_invalid_limit(self):
        """Test search with invalid limit fails"""
        url = reverse('api:spotify-search')
        response = self.client.get(url, {
            'query': 'test',
            'limit': 100  # Max is 50
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('api_view_users.views.spotify_service.get_track_info')
    def test_get_track_info(self, mock_get_track):
        """Test getting track information"""
        mock_get_track.return_value = {
            "id": "123",
            "name": "Test Song"
        }
        
        url = reverse('api:spotify-track-detail', kwargs={'track_id': '123'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_track.assert_called_once_with('123')
    
    @patch('api_view_users.views.spotify_service.get_track_info')
    def test_get_track_info_not_found(self, mock_get_track):
        """Test getting non-existent track returns 404"""
        mock_get_track.return_value = {"error": "Track not found"}
        
        url = reverse('api:spotify-track-detail', kwargs={'track_id': '999'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('api_view_users.views.spotify_service.get_artist_info')
    def test_get_artist_info(self, mock_get_artist):
        """Test getting artist information"""
        mock_get_artist.return_value = {
            "id": "123",
            "name": "Test Artist"
        }
        
        url = reverse('api:spotify-artist-detail', kwargs={'artist_id': '123'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_artist.assert_called_once_with('123')
    
    @patch('api_view_users.views.spotify_service.get_artist_top_tracks')
    def test_get_artist_top_tracks(self, mock_get_top):
        """Test getting artist top tracks"""
        mock_get_top.return_value = {
            "tracks": []
        }
        
        url = reverse('api:spotify-artist-top-tracks', kwargs={'artist_id': '123'})
        response = self.client.get(url, {'country': 'US'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_top.assert_called_once_with('123', 'US')
    
    def test_get_artist_top_tracks_invalid_country(self):
        """Test getting top tracks with invalid country code"""
        url = reverse('api:spotify-artist-top-tracks', kwargs={'artist_id': '123'})
        response = self.client.get(url, {'country': 'USA'})  # Should be 2 chars
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
