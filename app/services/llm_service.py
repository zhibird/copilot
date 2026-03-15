from __future__ import annotations

import re

import httpx

from app.core.config import Settings, get_settings
from app.core.exceptions import DomainValidationError


class LLMService:
    """LLM wrapper with a default local mock mode for beginner-friendly setup."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def answer_question(self, question: str, hits: list[dict[str, object]]) -> str:
        provider = self.settings.llm_provider.lower().strip()
        if provider == "mock":
            return self._mock_answer(question=question, hits=hits)

        return self._openai_compatible_answer(question=question, hits=hits)

    def _mock_answer(self, question: str, hits: list[dict[str, object]]) -> str:
        if not hits:
            return "没有检索到可用知识片段，暂时无法回答。"

        top_snippets: list[str] = []
        for hit in hits[:2]:
            raw = str(hit.get("content", "")).strip()
            snippet = re.sub(r"\s+", " ", raw)
            if snippet:
                top_snippets.append(snippet[:160])

        if not top_snippets:
            return "已检索到片段，但内容为空，无法生成答案。"

        merged = "；".join(top_snippets)
        return f"基于知识库检索结果，关于“{question}”的回答是：{merged}"

    def _openai_compatible_answer(self, question: str, hits: list[dict[str, object]]) -> str:
        if not self.settings.llm_api_key:
            raise DomainValidationError("LLM_API_KEY is required when llm_provider is not 'mock'.")

        context = self._build_context(hits)

        system_prompt = (
            "You are an enterprise copilot. Answer strictly based on the provided context. "
            "If context is insufficient, say so explicitly."
        )
        user_prompt = f"Question:\n{question}\n\nContext:\n{context}"

        base_url = self.settings.llm_base_url.rstrip("/")
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.settings.llm_temperature,
            "max_tokens": self.settings.llm_max_tokens,
        }

        try:
            response = httpx.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.settings.llm_timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise DomainValidationError(f"LLM request failed: {exc}") from exc

        body = response.json()
        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise DomainValidationError("LLM response format is invalid.") from exc

        answer = str(content).strip()
        if not answer:
            raise DomainValidationError("LLM returned an empty answer.")

        return answer

    def _build_context(self, hits: list[dict[str, object]]) -> str:
        if not hits:
            return "(no context)"

        lines: list[str] = []
        for idx, hit in enumerate(hits, start=1):
            doc_id = str(hit.get("document_id", ""))
            chunk_index = hit.get("chunk_index", "")
            content = str(hit.get("content", "")).strip()
            lines.append(f"[{idx}] doc={doc_id} chunk={chunk_index}: {content}")

        return "\n".join(lines)