"""
This program takes a spotify playlist, and writes all song names (nicely formatted) to a text file.
"""

import time
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def main():
    
    tic = time.time()

    global sp
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    playlist_name = 'clasico'
    playlist_id = '4WjU0YeCrRteF501YSFhY1'
    songs = get_songs_for_playlist(playlist_id)
    with open(f'results/json/{playlist_name}.json', 'w') as f:
        json.dump(songs, f, ensure_ascii=False, indent=2, separators=(',', ': '))

    toc = time.time()
    print(f'Elapsed time: {toc - tic:2f} seconds')
    return 0

def get_songs_for_playlist(playlist_id: str) -> list[dict]:
    """
    Returns a list of all songs in a playlist.
    """
    songs = []
    playlist = sp.playlist(playlist_id)
    for item in playlist['tracks']['items']:
        track = item['track']
        song = dict(
            title = track['name'],
            artists = [artist['name'] for artist in track['artists']]
        )
        songs.append(song)
    return songs


if __name__ == '__main__':
    main()
