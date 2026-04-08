import asyncio

from app.services.model_router import ModelRouter


def test_model_router_uses_primary_provider_when_available() -> None:
    router = ModelRouter()

    async def fake_ollama(prompt: str, model: str | None = None) -> dict:
        return {"text": "ok", "model": model}

    router.ollama.chat = fake_ollama  # type: ignore[method-assign]
    result = asyncio.run(router.generate(stage="frontend", prompt="hello"))
    assert result["provider"] == "ollama"
    assert result["stage"] == "frontend"


def test_model_router_falls_back_to_cloud_provider() -> None:
    router = ModelRouter()

    async def fail_ollama(prompt: str, model: str | None = None) -> dict:
        raise RuntimeError("ollama unavailable")

    async def fake_cloud(prompt: str) -> dict:
        return {"text": "cloud ok"}

    router.ollama.chat = fail_ollama  # type: ignore[method-assign]
    router._cloud_chat = fake_cloud  # type: ignore[method-assign]
    result = asyncio.run(router.generate(stage="quality", prompt="hello"))
    assert result["provider"] == "cloud"
    assert result["response"]["text"] == "cloud ok"
