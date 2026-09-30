import asyncio
import random

import httpx

from .config import FALLBACK_REASONING, OPENROUTER_BASE, REASONING_TOKEN_HEADROOM, api_key

RETRYABLE = {408, 429, 500, 502, 503, 504}


class OpenRouterError(Exception):
    pass


async def chat(
    client: httpx.AsyncClient,
    model: str,
    messages: list[dict],
    *,
    temperature: float,
    max_tokens: int,
    response_format: dict | None = None,
    attempts: int = 6,
) -> dict:
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "usage": {"include": True},
        "reasoning": {"enabled": False},
    }
    if response_format:
        body["response_format"] = response_format
    headers = {"Authorization": f"Bearer {api_key()}"}
    last_error = ""
    for attempt in range(attempts):
        try:
            resp = await client.post(f"{OPENROUTER_BASE}/chat/completions", headers=headers, json=body, timeout=90)
        except httpx.HTTPError as exc:
            last_error = repr(exc)
        else:
            payload = resp.json() if resp.content else {}
            error = payload.get("error")
            code = (error or {}).get("code", resp.status_code)
            if not error and resp.status_code == 200 and payload.get("choices"):
                return payload
            last_error = str(error or payload)[:300]
            if "Reasoning is mandatory" in last_error and body["reasoning"] != FALLBACK_REASONING:
                body["reasoning"] = FALLBACK_REASONING
                body["max_tokens"] = max_tokens + REASONING_TOKEN_HEADROOM
                continue
            if code not in RETRYABLE and resp.status_code not in RETRYABLE:
                raise OpenRouterError(last_error)
        await asyncio.sleep(min(60, 2**attempt) + random.random())
    raise OpenRouterError(last_error)
