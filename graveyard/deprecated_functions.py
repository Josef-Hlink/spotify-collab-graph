import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


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
