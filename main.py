"""
This program creates a graph that shows the collaboration between a given set of artists based on how many songs they have collaborated on.
For this, we use the spotipy and networkx libraries.
"""

import time
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# TODO
import networkx as nx


def main():

    tic = time.time()

    global sp
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    # playlist_name = 'amazing'
    # playlist_id = '0h9FqxtPsTl96WWHsoLCye'
    playlist_name = 'test'
    playlist_id = '034e7QTICexVCHgdEzL0J2'
    artists: dict[str, str] = get_artists_from_playlist(playlist_id)

    # find out the collaboration data
    df = create_dataframe(artists)

    # save the dataframe to a csv file
    df.to_csv(f'results/{playlist_name}_collaborations.csv')

    toc = time.time()
    print(f'Elapsed time: {toc - tic:2f} seconds')
    return 0


def create_dataframe(artists: dict[str, str]) -> pd.DataFrame:
    """   This is where most of the work is done.   """

    # the dataframe will essentially be a matrix, where each song is a row with two or more ones for its columns
    df = pd.DataFrame(columns=artists.keys())
    df.index.name = 'song_id'

    # for each artist, get their songs
    for artist_id, artist_name in artists.items():
        print(f'querying songs for "{artist_name}"...')
        song_ids: list[str] = get_songs_for_artist(artist_id)
        n = len(song_ids)
        # for each song, get the artists
        for i, song_id in enumerate(song_ids):
            print(f'\rprocessing songs {i+1}/{n}...', end='')
            artist_ids: list[str] = get_artist_ids_for_song(song_id)
            # filter artist_ids to contain only those that we are interested in
            artist_ids_filtered: list[str] = [artist_id for artist_id in artist_ids if artist_id in artists.keys()]
            # if the song has at least two artists we are interested in, add it to the dataframe
            if len(artist_ids_filtered) >= 2:
                df.loc[song_id, artist_ids_filtered] = 1
        print('\n-----------------')
    
    # convert all artist ids in df to names for readability
    # FIXME: sometimes multiple artist id's map to the same artist name
    # in this step it's not a huge problem, but it might be in the future
    df.columns = artists.values()
    # fill all NaNs with 0s
    df = df.fillna(0)
    
    return df


def get_artists_from_playlist(playlist_id: str) -> dict[str, str]:
    """   Finds the artists from a given playlist.   """

    # get all tracks
    tracks: dict = sp.playlist(playlist_id)['tracks']['items']
    # get all artists
    artists: dict[str, str] = {}
    for track in tracks:
        for artist in track['track']['artists']:
            artists[artist['id']] = artist['name']
    
    return artists

def get_artist_ids_for_song(song_id: str) -> list[str]:
    """   Finds the ids of the artists for a given song.   """

    # get the song's data
    song_data: dict = sp.track(song_id)
    # get the artists
    artists: dict = song_data['artists']
    # list comprehension to extract the ids of the artists
    artist_ids: list[str] = [artist['id'] for artist in artists]

    return artist_ids

def get_songs_for_artist(artist_id: str) -> list[str]:
    """   Finds the ids of the songs for a given artist.   """

    # get all artist's albums
    albums: dict = sp.artist_albums(artist_id)
    # get the ids of the albums
    album_ids: list[str] = [album['id'] for album in albums['items']]
    # initialize empty list
    song_ids: list[str] = []
    for album_id in album_ids:
        # for each album, get the songs
        songs: dict = sp.album_tracks(album_id)
        # filter out songs that only have one artist
        songs_filtered: list[str] = [song['id'] for song in songs['items'] if len(song['artists']) > 1]
        song_ids += songs_filtered

    return song_ids


if __name__ == '__main__':
    main()
