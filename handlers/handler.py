from abc import ABC, abstractmethod
from structure import OperationResult, HandlerResult

class BaseHandler(ABC):
    def __init__(self,
                 result: OperationResult,
                 expected: str | None) -> None:
        self.result = result
        self.expected = expected

    @abstractmethod
    def evaluate(self) -> HandlerResult:
        pass

