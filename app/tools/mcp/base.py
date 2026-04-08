from abc import ABC, abstractmethod
from typing import Any


class MCPTool(ABC):
    name: str

    @abstractmethod
    async def execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
