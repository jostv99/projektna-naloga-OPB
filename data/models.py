
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Uporabnik:
    id : int = field(default=0)
    ime : str = field(default='')
    priimek : str = field(default='')
    email : str = field(default='')
    kredibilnost : int = field(default=0)
    uporabnisko_ime : str = field(default='')
    telefon : str = field(default='')
    geslo : str = field(default='')
    kraj_bivanja : str = field(default='')
    sporocila : str = field(default='')


@dataclass_json
@dataclass
class Kategorija:
    id : int = field(default=0)
    opis : str = field(default='')


@dataclass_json
@dataclass
class Oglas:
    id : int = field(default=0)
    prodajalec : str = field(default='')
    kategorija : int = field(default=0)
    opis : str = field(default='')
    naslov : str = field(default='')
    cena : float = field(default=0)
    slika : str = field(default='')
