from textwrap import dedent

class Song:
    def __init__(self, id_: str, name: str, artist_ids: list[str]) -> None:
        self.id_: str = id_
        self.name: str = name
        self.artist_ids: list[str] = artist_ids
    
    def as_dict(self) -> dict:
        return {
            'id': self.id_,
            'name': self.name,
            'artist_ids': self.artist_ids
        }
    
    def __repr__(self) -> str:
        return dedent(
            f'''\
                name: {self.name}
                id: {self.id_}
                lead artist id: {self.artist_ids[0]}\
            '''
        )
