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

    artist_names = ['Chefket', 'Provinz', 'MAJAN', 'CRO','Makko','Tua','Lea','Casper','Trettmann']
    # this variable maps the names to their ids
    artists: dict[str, str] = get_artist_ids(artist_names)
    quit()
    df = create_dataframe(artists)

    # save the dataframe to a csv file
    df.to_csv('results/collaborations.csv')

    toc = time.time()
    print(f'Elapsed time: {toc - tic:2f} seconds')
    return 0

def get_artist_id_from_user() -> dict[str, str]:

def get_user_tracks():
    sp.current_user_saved_tracks(limit=1000, offset=0, market=None)

def create_dataframe(artists: dict[str, str]) -> pd.DataFrame:
    """   This is where most of the work is done.   """

    # the dataframe will essentially be a matrix, where each song is a row with two or more ones for its columns
    df = pd.DataFrame(columns=artists.values())
    df.index.name = 'song_id'

    # for each artist, get their songs
    for artist_name, artist_id in artists.items():
        print(f'querying songs for "{artist_name}"...')
        song_ids: list[str] = get_songs_for_artist(artist_id)
        n = len(song_ids)
        # for each song, get the artists
        for i, song_id in enumerate(song_ids):
            print(f'\rprocessing songs {i+1}/{n}...', end='')
            artist_ids: list[str] = get_artist_ids_for_song(song_id)
            # filter artist_ids to contain only those that we are interested in
            artist_ids_filtered: list[str] = [artist_id for artist_id in artist_ids if artist_id in artists.values()]
            # if the song has at least two artists we are interested in, add it to the dataframe
            if len(artist_ids_filtered) >= 2:
                df.loc[song_id, artist_ids_filtered] = 1
        print('\n-----------------')
    
    # convert all artist ids in df to names for readability
    df.columns = artists.keys()
    # fill all NaNs with 0s
    df = df.fillna(0)
    return df

def get_artist_ids(names: list[str]) -> dict[str, str]:
    """   Finds the ids of the artists using a standard query.   """

    # initialize empty dictionary
    ids = {}
    for name in names:
        # we do a simple query, similar to how you'd search for an artist in the app
        result: dict = sp.search(q='artist:' + name, type='artist', limit=1)
        # sp.search returns a pretty big dictionary, so we prune it down to just the artist's id
        artist_id: str = result['artists']['items'][0]['id']
        # update dictionary
        ids[name] = artist_id
        print(artist_id)
    return ids

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
