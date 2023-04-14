"""
    Este archivo contiene funciones para la interacción entre iTunes y Spotify.

Módulos importados:
    - plistlib
    - spotipy
    - spotipy.util
    - python-decouple

Autor: Daniel Rincón

Versión: 1.0
"""
import json
import plistlib
import spotipy
from spotipy import util
from decouple import config


def get_playlist_tracks(library, playlist_name):
    """Obtiene las pistas de una lista de en una biblioteca iTunes.

    Args:
        library (dict): Diccionario que representa la biblioteca iTunes.
        playlist_name (str): Nombre de la lista de reproducción.
    Returns:
        list: Una lista de diccionarios que representan las pistas de la
            lista de reproducción.
              Cada diccionario contiene información sobre la pista, como
              el artista, título, álbum y año.
    """
    playlist_tracks = []
    for playlist in library['Playlists']:
        if playlist['Name'] == playlist_name:
            for track in playlist['Playlist Items']:
                track_id = track['Track ID']
                playlist_tracks.append(library['Tracks'][str(track_id)])
            break
    return playlist_tracks


def obtain_itunes_songs(playlist_name):
    """Obtiene las canciones de una lista de reproducción de iTunes.

    La función obtiene las canciones de una lista de reproducción de
    iTunes (desde el XML) y las devuelve como una lista de diccionarios
    con la información del artista, título, álbum y año.

    Args:
        playlist_name (str): El nombre de la lista de reproducción en
            iTunes de la que se desean obtener las canciones.
    Returns:
        list: Una lista de diccionarios que contiene la información de
            las canciones de la lista de reproducción especificada.
            Cada diccionario contiene las siguientes claves:
            'artist' (str): El nombre del artista de la canción.
            'title' (str): El título de la canción.
            'album' (str): El nombre del álbum al que pertenece la canción.
            'year' (int): El año de lanzamiento de la canción.
    """
    xml_path = config('XML_PATH')
    with open(xml_path, 'rb') as xml_file:
        library = plistlib.load(xml_file)
    itunes_tracks = get_playlist_tracks(library, playlist_name)
    songs = []
    for track in itunes_tracks:
        artist = track['Artist']
        title = track['Name']
        album = track['Album']
        year = track['Year']
        song = {
            'artist': artist,
            'title': title,
            'album': album,
            'year': year
        }
        songs.append(song)
    return songs


class SpotifyConnection():
    """Clase que representa una conexión con la API de Spotify.

    Clase que establece conexión con la API de Spotify y ofrece métodos para
    crear una playlist en Spotify y añadir canciones a partir de una lista
    de canciones.
    Atributos:
        spotify (spotipy.Spotify): Objeto de la biblioteca Spotipy para
            interactuar con la API de Spotify.
        username (str): Nombre de usuario de Spotify utilizado para la
            conexión.

    Métodos:
        __init__(): Inicializa la conexión a la API de Spotify utilizando las
            credenciales proporcionadas en el archivo .env.
        obtain_spotify_songs(itunes_songs): Busca canciones de Spotify
            utilizando la información de las canciones de iTunes
            proporcionadas.
        create_spotify_playlist(playlist_name, playlist_description): Crea una
            nueva lista de reproducción pública en Spotify con el nombre y la
            descripción proporcionados.
        save_songs_in_playlist(playlist, spotify_tracks): Agrega las canciones
            de Spotify a la lista de reproducción especificada.
    """

    def __init__(self):
        """Inicializa la instancia de la clase SpotifyConnection.

        Obtiene el token de acceso a la API de Spotify y guarda la instancia
        de Spotify.
        """
        client_id = config('CLIENT_ID')
        client_secret = config('CLIENT_SECRET')
        redirect_uri = config('REDIRECT_URI')
        username = config('USER_NAME')
        scope = 'playlist-modify-public'
        token = util.prompt_for_user_token(
            username, scope, client_id=client_id,
            client_secret=client_secret, redirect_uri=redirect_uri)
        if not token:
            raise ValueError("""No se pudo obtener el token de acceso.
                Asegúrese de haber proporcionado las credenciales
                correctas en el archivo .env.""")
        self.spotify = spotipy.Spotify(auth=token)
        self.username = username

    def obtain_spotify_songs(self, itunes_songs):
        """Busca canciones de spotify a partir de un listado.

        Busca las canciones de iTunes en Spotify teniendo en cuenta el artista,
        el título de la canción, el año y el album  y retorna una lista de las
        canciones encontradas y una lista de las canciones no encontradas.

        Args:
            itunes_songs (list): lista de diccionarios con información de
                canciones de iTunes
        Returns:
            tuple: tupla con dos listas, una de las canciones encontradas
                y otra de las canciones no encontradas
        """
        spotify_tracks = []
        empty_tracks = []
        for track in itunes_songs:
            title = track['title'].replace("'", "")
            query = f"artist:{track['artist']} track:{title} " \
                f"album:{track['album']} year:{track['year']}"
            result = self.spotify.search(q=query, type='track', limit=1)
            if len(result['tracks']['items']) > 0:
                spotify_tracks.append(result['tracks']['items'][0]['uri'])
            else:
                query = f"artist:{track['artist']} track:{title}"
                result = self.spotify.search(q=query, type='track', limit=1)
                if len(result['tracks']['items']) > 0:
                    spotify_tracks.append(result['tracks']['items'][0]['uri'])
                else:
                    # No encontró la canción por ninguno de los métodos
                    empty_tracks.append(track)
        return spotify_tracks, empty_tracks

    def create_spotify_playlist(self, playlist_name, playlist_description):
        """Crea una playlist asociada a la cuenta de Spotify del usuario.

        Crea una nueva playlist en la cuenta de Spotify del usuario y retorna
            la información de la playlist creada.

        Args:
            playlist_name (str): nombre de la nueva playlist
            playlist_description (str): descripción de la nueva playlist
        Returns:
            dict: diccionario con la información de la playlist creada
        """
        playlist = self.spotify.user_playlist_create(
            self.username, playlist_name, public=True,
            description=playlist_description)
        return playlist

    def save_songs_in_playlist(self, playlist, spotify_tracks):
        """Agrega las canciones a la playlist creada en Spotify.

        Arguments:
            playlist (dict): diccionario con la información de la playlist
                creada en Spotify.
            spotify_tracks (list): lista de URI de las canciones de Spotify
                a agregar a la playlist.
        """
        tracks_batches = [
            spotify_tracks[i:i+99] for i in range(0, len(spotify_tracks), 99)]
        for tracks_batch in tracks_batches:
            self.spotify.user_playlist_add_tracks(
                self.username, playlist['id'], tracks_batch)


if __name__ == "__main__":
    # Definimos el nombre y descripción de la lista de reproducción en Spotify
    PLAYLIST_NAME = config('PLAYLIST_NAME')
    PLAYLIST_DESCRIPTION = config('PLAYLIST_DESCRIPTION')
    # Obtenemos las canciones de iTunes
    tracks = obtain_itunes_songs(PLAYLIST_NAME)
    # Creamos una instancia de la clase SpotifyConnection
    conn = SpotifyConnection()
    # Buscamos las canciones en Spotify y obtenemos las encontradas
    # y las no encontradas
    spotify_songs, empty_songs = conn.obtain_spotify_songs(tracks)
    # Creamos la lista de reproducción en Spotify
    playlist_spotify = conn.create_spotify_playlist(
        PLAYLIST_NAME, PLAYLIST_DESCRIPTION)
    # Agregamos las canciones a la lista de reproducción en Spotify
    conn.save_songs_in_playlist(playlist_spotify, spotify_songs)
    # Guardamos las canciones que no se encontraron en un json
    with open("empty_songs.json", "w", encoding='UTF-8') as f:
        json.dump(empty_songs, f)
