from datetime import datetime
from dataclasses import dataclass


@dataclass
class Item:
    pass


@dataclass
class Tune(Item):
    added: datetime
    title: str
    arranger: str
    composer: str
    data: bytes
