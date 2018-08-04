from .base import Serializer
from .kettle import KettleSerializer
from .meltano import MeltanoSerializer


serializer_map = {
    'meltano': MeltanoSerializer,
    'kettle': KettleSerializer,
}


def serializer_for(name: str, *args) -> Serializer:
    return serializer_map[name](*args)
