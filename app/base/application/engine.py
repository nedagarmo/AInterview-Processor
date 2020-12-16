from typing import List
from ..abstract import IEngine, IModel
from .result import ResultProcess


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

    __results: List[ResultProcess] = []

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
            result: ResultProcess = observer.update(self.__frame)
            if result is not None:
                self.__results.append(result)

    def process(self, frame: bytes) -> None:
        """
        Method that updates the frame to be processed and
        triggers the notification to the observers
        """
        self.__frame = frame
        self.notify()

    def results(self) -> List[ResultProcess]:
        """
        Method that return the results
        """
        returnable = self.__results.copy()
        self.__results.clear()
        return returnable
