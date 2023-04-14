# iTunes-to-Spotify

Este repositorio contiene un script en Python que te permite obtener las canciones de una lista de reproducción de iTunes y buscarlas en Spotify, para crear automáticamente una nueva lista de reproducción en tu cuenta de Spotify con las canciones encontradas.

## Requisitos
Para ejecutar el script, necesitarás tener instalado Python en tu equipo y las siguientes bibliotecas de Python:

- json
- plistlib
- spotipy
- decouple

Además, necesitarás tener una cuenta de desarrollador en Spotify para obtener las credenciales de acceso.

## Configuración
Antes de ejecutar el script, deberás configurar las siguientes variables de entorno en un archivo .env:

- CLIENT_ID: tu ID de cliente de Spotify
- CLIENT_SECRET: tu secreto de cliente de Spotify
- REDIRECT_URI: la URI de redireccionamiento para la autorización de Spotify
- USER_NAME: tu nombre de usuario de Spotify
- XML_PATH: la ruta del archivo XML de iTunes que contiene la lista de reproducción que deseas importar

## Uso
1. Instalar los paquetes necesarios:
```
pip install requirements.txt
```
2. Crear las variables de entorno en un archivo "*.env*"
```dotenv
CLIENT_ID='your-client-id'
CLIENT_SECRET='your-client-secret'
REDIRECT_URI='your-redirect-uri'
USER_NAME='your-Spotify-username'
XML_PATH='your-iTunes-xml-file-path'
PLAYLIST_NAME='your-iTunes-playlist-name (and Spotify)'
PLAYLIST_DESCRIPTION="""Your Spotify playlist description."""
```
3. Simplemente ejecutar:
```python
python main.py
```
El script te guiará a través del proceso de lectura de la lista de reproducción en iTunes, su listado de canciones, la autenticación con Spotify y la creación de la lista de reproducción en Spotify a partir de la lista de iTunes, las canciones no encontradas las guarda en un archivo llamado *empty_songs.json*.

## Contribuciones
Las contribuciones a este proyecto son bienvenidas. Si deseas contribuir, puedes abrir un PR o crear un issue.

## Licencia
Este proyecto está licenciado bajo la licencia MIT.