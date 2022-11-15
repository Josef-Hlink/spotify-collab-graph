from textwrap import dedent

class Artist:
    def __init__(self, id_: str, name: str) -> None:
        self.id_: str = id_
        self.name: str = name
        self.occurrences: int = 1

    def as_dict(self) -> dict:
        return {
            'id': self.id_,
            'name': self.name,
            'occurrences': self.occurrences
        }

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Artist):
            return self.id_ == other.id_
        return False

    def __hash__(self) -> int:
        return hash(self.id_)
    
    def __repr__(self) -> str:
        return dedent(
            f'''\
                name: {self.name}
                id: {self.id_}
                occurrences: {self.occurrences}\
            '''
        )
