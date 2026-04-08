from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    name: str

    @abstractmethod
    async def handle(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
