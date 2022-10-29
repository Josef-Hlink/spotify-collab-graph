"""
This program creates a graph that shows the collaboration between a given set of artists based on how many songs they have collaborated on.
For this, we use the spotipy and networkx libraries.
"""
import time
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
scope = 'user-library-read'

import networkx as nx
# TODO
# write down and refactor code to be readable

def main():

    tic = time.time()
    global sp
    #use the scope argument when retrieving user data, use the other one when artists.csv has been generated for faster runtime.
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    #sp = spotipy.Spotify(auth_manager=SpotifyOAuth())

    #running this block once gets all the artist names and IDs from a user's saved songs and exports it to csv.
    #artists = get_user_artists_from_saved_songs()
    #df_artists = pd.DataFrame(list(artists.items()), columns = ['name', 'id'])
    #df_artists.to_csv('results/artists.csv')

    #when you have a list of the artists saved, running this block will convert it back to the right dictionary format and enter it into
    # the collaboration matrix generator
    df_artists = pd.read_csv('results/artists.csv')
    dict_artists = df_to_dict(df_artists)
    df_coll = create_dataframe(dict_artists)
    df_coll.to_csv('results/collaborations.csv')
    toc = time.time()
    print(f'Elapsed time: {toc - tic:2f} seconds')
    return 0

#This function takes the csv file containing artist data and converts it back to the right dictionary format
def df_to_dict(dfa: pd.DataFrame) -> dict[str,str]:
    dfa.reset_index(drop=True)
    artists = {}
    names = list(dfa['name'])
    ids = list(dfa['id'])
    for name in names:
        artists[name] = ids[names.index(name)]
    return artists

# loops over the first 1000 saved songs and returns a list of dictionaries of the format {'name': 'artist_name', 'id': 'artist ID'}
def get_user_artists_from_saved_songs() -> dict[str,str]:
    #initialise artist ids
    ids = {}

    #sp.current_user_saved_tracks has a limit of 50 tracks at once 
    #the offset parameter starts the data collection further down the list of tracks, so by iterating this in steps of 50 
    #you can get the whole list of saved songs. A range of 21 was chosen here to retrieve the first 1000 songs (out of 10000 max)
    #The saved tracks get returned as a dictionary containing entries with info about the request and the 'items' entry containing the songs
    #the items entry is split into the 'date added' and 'track' entries, with the 'track entry' again containing subentries describing the artist, album, and track id etc

    #for this step we are only interested in retrieving the artists that the user listens to, so we loop over each song and save only the artist name and ID.
    for offset in range(0,21):
        saved_songs: dict = sp.current_user_saved_tracks(limit=50, offset=50*offset, market=None)
        for song in saved_songs['items']:
                for artist in song['track']['artists']:
                    ids[artist['name']] = artist['id']
    return ids

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
