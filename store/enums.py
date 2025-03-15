from typing import Dict, Any
from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def dict(cls) -> Dict[str, Any]:
        return {e.name: e.value for e in cls}

    @classmethod
    def keys(cls) -> list:
        return [e.name for e in cls]

    @classmethod
    def choices(cls) -> list:
        return [(e.name, e.value) for e in cls]

    @classmethod
    def values(cls) -> list:
        return [i.value for i in cls]

    @classmethod
    def get_value(cls, key: str) -> Any:
        if not hasattr(cls, key):
            raise KeyError(
                f'Invalid key {key}, valid keys are: {", ".join(cls.keys())}'
            )
        return getattr(cls, key).value

    @classmethod
    def get_name(cls, value):
        return cls(value).name
