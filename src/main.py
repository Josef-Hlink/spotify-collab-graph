"""
This program creates a graph that shows the collaboration between a given set of artists based on how many songs they have collaborated on.
For this, we use the spotipy and networkx libraries.
"""

import time
import json

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import matplotlib.pyplot as plt
import networkx as nx

from artist import Artist
from song import Song


def main():

    tic = time.time()

    global SP
    SP = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    global CALLS
    CALLS = 0

    playlist_name = 'amazing'
    playlist_id = '0h9FqxtPsTl96WWHsoLCye'
    # playlist_name = 'test'
    # playlist_id = '034e7QTICexVCHgdEzL0J2'
    artists = get_artists_for_playlist(playlist_id)
    print(f'Found {len(artists)} artists in the "{playlist_name}" playlist.')

    # find out the collaboration data
    df = create_dataframe(artists)

    # save the dataframe to a csv file
    df.to_csv(f'../results/csv/{playlist_name}_collaborations.csv')

    toc = time.time()
    print(f'Elapsed time: {toc - tic:2f} seconds')
    print(f'Number of API calls made: {CALLS}')

    df = pd.read_csv(f'../results/csv/{playlist_name}_collaborations.csv', index_col='song_id')
    # drop columns with only only zeros
    nw = create_network(df)
    fig, ax = plt.subplots(figsize=(10, 10))
    nx.draw(nw, with_labels=True, ax=ax)
    fig.tight_layout()
    fig.savefig(f'../results/png/{playlist_name}_collaborations.png')

    return 0


def create_network(df: pd.DataFrame) -> nx.Graph:
    """   Creates a networkx graph from the dataframe.   """

    # create a graph
    G = nx.Graph()
    # add nodes
    G.add_nodes_from(df.columns)
    # add edges
    for i, row in df.iterrows():
        # get the artists for this song
        artists = row[row == 1].index
        # add edges between all artists
        G.add_edges_from([(artists[i], artists[j]) for i in range(len(artists)) for j in range(i+1, len(artists))])
    
    # increase spacing between nodes
    pos = nx.spring_layout(G, k=0.7)
    nx.set_node_attributes(G, pos, 'pos')

    return G


def create_dataframe(artists: list[Artist]) -> pd.DataFrame:
    """   This is where most of the work is done.   """

    # the dataframe will essentially be a matrix, where each song is a row with two or more ones for its columns
    artist_ids = [artist.id_ for artist in artists]
    artist_names = [artist.name for artist in artists]
    df = pd.DataFrame(columns=artist_ids)
    df.index.name = 'song_id'

    for artist in artists:
        for song in get_relevant_songs_for_artist(artist, artist_ids):
            df.loc[song.id_, song.artist_ids] = 1
    
    # convert all artist ids in df to names for readability
    # FIXME: sometimes multiple artist id's map to the same artist name
    # in this step it's not a huge problem, but it might be in the future
    df.columns = artist_names
    # fill all NaNs with 0s
    df = df.fillna(0)
    # drop artists that have no collaborations
    df = df.loc[:, (df != 0).any(axis=0)]

    return df


def get_artists_for_playlist(playlist_id: str) -> list[Artist]:
    """   Finds the artists from a given playlist.   """

    # get all songs
    songs: dict = sp_playlist(playlist_id)['tracks']['items']

    artists: list[Artist] = []
    for song in songs:
        # add each artist to the list
        for artist in song['track']['artists']:
            # create an Artist object
            artist_obj: Artist = Artist(artist['id'], artist['name'])
            # if the artist is already in the list, increment the occurrences
            if artist_obj in artists:
                artists[artists.index(artist_obj)].occurrences += 1
            # otherwise, add it to the list
            else:
                artists.append(artist_obj)
    
    return artists

def get_relevant_songs_for_artist(artist: Artist, all_artist_ids: list[str]) -> list[Song]:
    """   Finds all relevant songs for a given artist.   """

    print(f'querying songs for "{artist.name}"...')

    # cast all_artist_ids to a set for faster lookup
    all_artist_ids = set(all_artist_ids)

    # get all albums for the artist
    album_ids: list[str] = [album['id'] for album in sp_artist_albums(artist.id_)['items']]
    # request all albums at once
    albums: list[dict] = sp_albums(album_ids)['albums']
    # unwrap all songs from the albums
    songs: list[dict] = [track for album in albums for track in album['tracks']['items']]
    n = len(songs)

    relevant_songs: list[str] = []
    for i, song in enumerate(song):
        print(f'\rprocessing song {i+1}/{n}...', end='')
        # get the artists for this song
        artist_ids: list[str] = [artist['id'] for artist in song['artists']]
        # if the song has at least two artists we are interested in, add it to the list as a Song object
        artist_ids_in_playlist = [artist_id for artist_id in artist_ids if artist_id in all_artist_ids]
        if len(artist_ids_in_playlist) >= 2:
            song_obj = Song(song['id'], song['name'], artist_ids_in_playlist)
            relevant_songs.append(song_obj)
    print('\n-----------------')

    return relevant_songs


def api_call(func):
    """   Wrapper for the Spotify API calls.   """
    def wrapper(*args, **kwargs):
        global CALLS
        CALLS += 1
        return func(*args, **kwargs)
    return wrapper

@api_call
def sp_playlist(playlist_id: str) -> dict:
    return SP.playlist(playlist_id)

@api_call
def sp_artist_albums(artist_id: str) -> dict:
    return SP.artist_albums(artist_id, limit=50)

@api_call
def sp_albums(album_ids: list[str]) -> dict:
    return SP.albums(album_ids)

if __name__ == '__main__':
    main()
