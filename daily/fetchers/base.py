"""Shared pieces for fetchers."""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

from daily.config import SourceConfig
from daily.models import Candidate
from daily.window import Window

SUMMARY_MAX_CHARS = 1500

Fetcher = Callable[[httpx.AsyncClient, SourceConfig, Window], Awaitable[list[Candidate]]]

# Used by community/trending sources to keep only AI-related items. Word-boundary matched,
# case-insensitive; multi-word entries match as phrases.
AI_KEYWORDS = [
    "ai",
    "llm",
    "llms",
    "gpt",
    "agent",
    "agents",
    "agentic",
    "rag",
    "mcp",
    "transformer",
    "transformers",
    "diffusion",
    "inference",
    "embedding",
    "embeddings",
    "fine-tune",
    "fine-tuning",
    "finetune",
    "lora",
    "prompt",
    "chatbot",
    "neural",
    "machine learning",
    "deep learning",
    "language model",
    "vision-language",
    "vlm",
    "multimodal",
    "reasoning model",
    "openai",
    "anthropic",
    "claude",
    "gemini",
    "deepmind",
    "llama",
    "mistral",
    "qwen",
    "deepseek",
    "kimi",
    "grok",
    "copilot",
    "hugging face",
    "huggingface",
    "pytorch",
    "cuda",
    "vllm",
    "ollama",
    "llama.cpp",
    "gguf",
    "text-to-speech",
    "tts",
    "speech recognition",
    "asr",
    "stable diffusion",
    "codex",
    "tokenizer",
    "rlhf",
    "reinforcement learning",
]
_AI_PATTERN = re.compile(
    r"(?<![a-z0-9])("
    + "|".join(re.escape(k) for k in sorted(AI_KEYWORDS, key=len, reverse=True))
    + r")(?![a-z0-9])",
    re.I,
)


def is_ai_related(*texts: str | None, extra_keywords: list[str] | None = None) -> bool:
    blob = " ".join(t for t in texts if t)
    if _AI_PATTERN.search(blob):
        return True
    return any(k.lower() in blob.lower() for k in extra_keywords or [])


def candidate(source: SourceConfig, **fields: Any) -> Candidate:
    return Candidate(source=source.id, source_name=source.name, tier=source.tier, kind=source.kind, **fields)


async def get(client: httpx.AsyncClient, url: str, **kwargs: Any) -> httpx.Response:
    response = await client.get(url, **kwargs)
    response.raise_for_status()
    return response
