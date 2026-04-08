from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings
from app.services.llm import LLMClient


class ModelRouterError(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelRoute:
    stage: str
    primary_provider: str
    fallback_provider: str


class ModelRouter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.ollama = LLMClient()

    def _route_for_stage(self, stage: str) -> ModelRoute:
        preferred = self.settings.web_builder_primary_provider
        fallback = self.settings.web_builder_fallback_provider
        # Keep stage-aware override simple and predictable for phase 1.
        if stage in {"design", "frontend", "quality"} and self.settings.web_builder_force_cloud_for_design:
            preferred = "cloud"
            fallback = "ollama"
        return ModelRoute(stage=stage, primary_provider=preferred, fallback_provider=fallback)

    async def generate(self, *, stage: str, prompt: str) -> dict[str, Any]:
        route = self._route_for_stage(stage)
        tried_errors: list[str] = []

        for provider in (route.primary_provider, route.fallback_provider):
            try:
                if provider == "ollama":
                    result = await self.ollama.chat(prompt)
                elif provider == "cloud":
                    result = await self._cloud_chat(prompt)
                else:
                    raise ModelRouterError(f"Unsupported provider '{provider}'")
                return {"provider": provider, "stage": stage, "response": result}
            except Exception as exc:  # noqa: BLE001 - keep complete provider failure reason.
                tried_errors.append(f"{provider}: {exc}")

        raise ModelRouterError(
            f"All providers failed for stage '{stage}'. Failures: {', '.join(tried_errors)}"
        )

    async def _cloud_chat(self, prompt: str) -> dict[str, Any]:
        if not self.settings.cloud_llm_base_url:
            raise ModelRouterError("CLOUD_LLM_BASE_URL is not configured")
        if not self.settings.cloud_llm_api_key:
            raise ModelRouterError("CLOUD_LLM_API_KEY is not configured")

        headers = {
            "Authorization": f"Bearer {self.settings.cloud_llm_api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.settings.cloud_llm_model, "input": prompt}
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.cloud_llm_base_url.rstrip('/')}/v1/generate",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
