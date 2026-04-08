import contextlib
import os
from typing import Any, AsyncIterator

from mcp import ClientSession
from mcp.client.sse import sse_client

from app.core.config import get_settings

settings = get_settings()


class MCPClientManager:
    def __init__(self) -> None:
        self.sessions: dict[str, ClientSession] = {}
        self._contexts: dict[str, Any] = {}

    @contextlib.asynccontextmanager
    async def connect_sse(self, name: str, url: str, token: str | None = None) -> AsyncIterator[ClientSession]:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with sse_client(url, headers=headers) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                self.sessions[name] = session
                yield session
                self.sessions.pop(name, None)

    async def get_all_tools(self) -> list[dict[str, Any]]:
        tools = []
        for name, session in self.sessions.items():
            response = await session.list_tools()
            for tool in response.tools:
                tools.append({
                    "server": name,
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                })
        return tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict[str, Any]) -> Any:
        if server_name not in self.sessions:
            raise ValueError(f"MCP server '{server_name}' is not connected.")
        
        session = self.sessions[server_name]
        result = await session.call_tool(tool_name, arguments)
        return result

# Global manager instance
mcp_manager = MCPClientManager()
