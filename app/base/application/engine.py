from typing import List
from ..abstract import IEngine, IModel


class ModelEngine(IEngine):
    """
    The Subject owns some important state and notifies observers when the state
    changes.
    """

    __frame: bytes = None
    """
    For the sake of simplicity, the Subject's state, essential to all
    subscribers, is stored in this variable.
    """

    __observers: List[IModel] = []
    """
    List of subscribers. In real life, the list of subscribers can be stored
    more comprehensively (categorized by event type, etc.).
    """

    def attach(self, observer: IModel) -> None:
        self.__observers.append(observer)

    def detach(self, observer: IModel) -> None:
        self.__observers.remove(observer)

    """
    The subscription management methods.
    """

    def notify(self) -> None:
        """
        Trigger an update in each subscriber.
        """
        for observer in self.__observers:
            observer.update(self.__frame)

    def process(self, frame: bytes) -> None:
        """
        Method that updates the frame to be processed and
        triggers the notification to the observers
        """
        self.__frame = frame
        self.notify()
