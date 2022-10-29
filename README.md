# Spotify Collaboration Graph

This is a project to create a graph of the collaborations between artists on Spotify.
The data is collected from the Spotify API through [Spotipy](https://spotipy.readthedocs.io/en/master/) and the graph is created using the [NetworkX](https://networkx.org) library.


## Usage

Create a spotify developer account if you don't already have one.
Create a new app and get the client id and client secret.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export SPOTIPY_CLIENT_ID="your-spotify-client-id"
export SPOTIPY_CLIENT_SECRET="your-spotify-client-secret"
export SPOTIPY_REDIRECT_URI="your-app-redirect-url"

python3 main.py
```

The redirect url can just be `http://localhost:8888/callback/` for testing.


## Dependencies

- [Spotipy](https://spotipy.readthedocs.io/en/master/)
- [Pandas](https://pandas.pydata.org/)
- [NetworkX](https://networkx.org)

## To Do

- [core] create graph visualization
- [feature] query artists from a spotify playlist
- [enhancement] improve performance (Pandas → NumPy)


## License

[MIT](https://choosealicense.com/licenses/mit/)


