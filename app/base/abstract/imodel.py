from __future__ import annotations
from abc import ABC, abstractmethod


class IModel(ABC):
    """
    The Observer interface declares the update method, used by IObservable.
    """

    @abstractmethod
    def update(self, frame: bytes) -> None:
        """
        Receive update from subject.
        """
        pass
