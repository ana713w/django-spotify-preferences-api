import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()


class SpotifyService:
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpotifyService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Las credenciales de Spotify no están configuradas. "
                "Por favor, añade SPOTIFY_CLIENT_ID y SPOTIFY_CLIENT_SECRET a tu archivo .env"
            )
        
        self.token = None
        self.token_expires_at = None
        self.base_url = "https://api.spotify.com/v1"
        self._get_access_token()
        self._initialized = True
    
    def _get_access_token(self):
        auth_url = "https://accounts.spotify.com/api/token"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(auth_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.token = token_data["access_token"]
            
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            print("Token de Spotify listo")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error al obtener token de Spotify: {str(e)}")
    
    def _is_token_expired(self):
        if self.token_expires_at is None:
            return True
        return datetime.now() >= self.token_expires_at
    
    def _refresh_token_if_needed(self):
        if self._is_token_expired():
            print("Renovando token expirado...")
            self._get_access_token()
    
    def _make_request(self, method, url, params=None, max_retries=2):
        retries = 0
        
        while retries <= max_retries:
            try:
                self._refresh_token_if_needed()
                headers = {"Authorization": f"Bearer {self.token}"}
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 401:
                    if retries < max_retries:
                        print(f"Error 401, renovando token... (intento {retries + 1})")
                        self._get_access_token()
                        retries += 1
                        continue
                    else:
                        return {"error": "Autenticación falló después de reintentos"}
                
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401 and retries < max_retries:
                    retries += 1
                    continue
                return {"error": f"Error: {e.response.status_code}"}
            except Exception as e:
                return {"error": f"Error en petición: {str(e)}"}
    
    def search(self, query, search_type="track", limit=10):
        url = f"{self.base_url}/search"
        params = {"q": query, "type": search_type, "limit": limit}
        return self._make_request("GET", url, params=params)
    
    def get_track_info(self, track_id):
        url = f"{self.base_url}/tracks/{track_id}"
        return self._make_request("GET", url)
    
    def get_artist_info(self, artist_id):
        url = f"{self.base_url}/artists/{artist_id}"
        return self._make_request("GET", url)
    
    def get_artist_top_tracks(self, artist_id, country="US"):
        url = f"{self.base_url}/artists/{artist_id}/top-tracks"
        params = {"country": country}
        return self._make_request("GET", url, params=params)


spotify_service = SpotifyService()
