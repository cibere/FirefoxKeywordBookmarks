from __future__ import annotations

from typing import Self

from .options import Option

__all__ = ("Dataclass",)


class Dataclass:
    def to_option(self) -> Option:
        raise RuntimeError("This must be overriden")