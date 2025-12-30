# 🎵 Spotify Preferences API - Django

API REST desarrollada con Django REST Framework que permite gestionar usuarios y sus preferencias musicales, integrándose con la API de Spotify para obtener información de canciones y artistas.

## 📋 Requisitos Previos

- Python 3.8 o superior
- Cuenta de desarrollador de Spotify (para obtener credenciales de API)

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/ana713w/django-spotify-preferences-api
cd django-spotify-preferences-api
```

### 2. Crear y activar entorno virtual

**En Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

O manualmente:
```bash
pip install django
pip install djangorestframework
pip install python-dotenv
pip install requests
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la carpeta `backend/` basándote en `.env.example`:

```bash
cd backend
cp .env.example .env
```

Edita el archivo `.env` y agrega tus credenciales:

```env
# Django
SECRET_KEY=tu_secret_key_generada
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Spotify
SPOTIFY_CLIENT_ID=tu_client_id_aqui
SPOTIFY_CLIENT_SECRET=tu_client_secret_aqui
```

**Para obtener las credenciales de Spotify:**

1. Ve a [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Inicia sesión con tu cuenta de Spotify
3. Crea una nueva aplicación
4. Copia el **Client ID** y **Client Secret**
5. Pégalos en tu archivo `.env`

**Para generar una SECRET_KEY segura:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Ejecutar migraciones

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear tu cuenta de administrador.

### 7. Ejecutar la aplicación

```bash
python manage.py runserver
```

La API estará disponible en: **http://127.0.0.1:8000**

---

## 📚 Documentación de la API

Una vez que la aplicación esté corriendo, puedes acceder a:

- **API Root:** http://127.0.0.1:8000/
- **Panel de Administración:** http://127.0.0.1:8000/admin/
- **API Endpoints:** http://127.0.0.1:8000/api/

---

## 🔌 Endpoints Disponibles

### Endpoint Principal

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información de bienvenida y versión de la API |

### Usuarios (`/api/users`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/users/` | Crear un nuevo usuario |
| GET | `/api/users/` | Listar todos los usuarios |
| GET | `/api/users/{user_id}/` | Obtener un usuario específico por ID |
| PUT | `/api/users/{user_id}/` | Actualizar datos de un usuario |
| DELETE | `/api/users/{user_id}/` | Eliminar un usuario |
| GET | `/api/users/{user_id}/preferences/` | Obtener las preferencias musicales de un usuario |

### Preferencias Musicales (`/api/music`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/music/preferences/` | Crear una nueva preferencia musical |
| DELETE | `/api/music/preferences/{preference_id}/` | Eliminar una preferencia musical |

### Integración con Spotify (`/api/music/spotify`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/music/spotify/search/` | Buscar canciones, artistas o álbumes en Spotify |
| GET | `/api/music/spotify/track/{track_id}/` | Obtener información detallada de una canción |
| GET | `/api/music/spotify/artist/{artist_id}/` | Obtener información detallada de un artista |
| GET | `/api/music/spotify/artist/{artist_id}/top-tracks/` | Obtener las canciones más populares de un artista |

---

## 🧪 Testing con Postman

El proyecto incluye una colección de Postman con todos los endpoints configurados:

1. Importa la colección: `Spotify_Preferences_API_Django.postman_collection.json`
2. Importa el environment: `Spotify_API_Django_Environment.postman_environment.json`
3. Configura las variables como `base_url` (por defecto: `http://localhost:8000`)

---

## 🧪 Tests Automatizados

El proyecto incluye 29 tests automatizados que cubren:

- ✅ Modelos (User, MusicPreference)
- ✅ API de Usuarios (CRUD completo)
- ✅ API de Preferencias Musicales
- ✅ Integración con Spotify

**Ejecutar todos los tests:**

```bash
python manage.py test
```

---

## 📁 Estructura del Proyecto

```
django-spotify-preferences-api/
│
├── backend/
│   ├── manage.py                 # Punto de entrada de Django
│   ├── .env                      # Variables de entorno (no incluido en git)
│   ├── .env.example             # Ejemplo de variables de entorno
│   ├── db.sqlite3               # Base de datos SQLite
│   │
│   ├── api_server/              # Proyecto principal
│   │   ├── settings.py          # Configuración de Django
│   │   ├── urls.py              # URLs principales
│   │   └── wsgi.py              # WSGI para despliegue
│   │
│   └── api_view_users/          # App principal
│       ├── models.py            # Modelos (User, MusicPreference)
│       ├── serializers.py       # Serializadores para validación
│       ├── views.py             # Vistas de la API
│       ├── urls.py              # URLs de la app
│       ├── services.py          # Servicio de Spotify
│       ├── admin.py             # Configuración del admin
│       └── tests.py             # Tests automatizados
│
├── postman_collection/
│   ├── Spotify_Preferences_API_Django.postman_collection.json
│   └── Spotify_API_Django_Environment.postman_environment.json
│
├── requirements.txt             # Dependencias del proyecto
├── .gitignore                  # Archivos a ignorar en git
└── README.md                   # Este archivo
```

---

## 🛠️ Tecnologías Utilizadas

- **Django 5.1.3:** Framework web de alto nivel para Python
- **Django REST Framework 3.15.2:** Toolkit para construir Web APIs
- **Spotify Web API:** Integración con Spotify para obtener datos musicales
- **Python Dotenv:** Gestión de variables de entorno

## 📝 Notas Importantes

### Renovación Automática de Token de Spotify

El servicio de Spotify implementa renovación automática de tokens:

- ✅ Detecta automáticamente errores 401 (Unauthorized)
- ✅ Renueva el token automáticamente
- ✅ Reintenta la petición hasta 2 veces
- ✅ Renueva proactivamente antes de expirar (1 hora)

---

## 🚀 Ejemplos de Uso

### Crear un usuario

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe"
  }'
```

### Buscar una canción en Spotify

```bash
curl "http://localhost:8000/api/music/spotify/search/?query=bohemian%20rhapsody&type=track&limit=5"
```

### Crear una preferencia musical

```bash
curl -X POST http://localhost:8000/api/music/preferences/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "track_id": "3z8h0TU7ReDPLIbEnYhWZb"
  }'
```

La API automáticamente obtendrá la información de la canción desde Spotify.

---


