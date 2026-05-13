"""
Gemini generateContent with multi-model fallback.

Older IDs like gemini-1.5-flash often return 404 on v1beta after Google rotates models;
404 is raised on generate_content, not on GenerativeModel(), so we try each candidate in order.

429 / quota on free tier is often **per model per day** — we skip to the next candidate instead of
failing immediately. Optional short sleep when the API returns "retry in Xs".
"""

from __future__ import annotations

import os
import re
import time
from typing import Any, List, Optional, Tuple

# Order matters: Google counts quota **per model**. Put Gemini 3 / Flash-Lite first so we
# do not burn gemini-2.5-flash when AI Studio still shows headroom on "Gemini 3 Flash".
# See: https://ai.google.dev/gemini-api/docs/models
_DEFAULT_CANDIDATES = (
    "gemini-3.1-flash-lite,"
    "gemini-3-flash-preview,"
    "gemini-3.1-flash-lite-preview,"
    "gemini-2.5-flash-lite,"
    "gemini-2.0-flash,"
    "gemini-2.0-flash-001,"
    "gemini-2.5-flash,"
    "gemini-2.5-pro,"
    "gemini-1.5-flash-latest,"
    "gemini-1.5-flash-002,"
    "gemini-1.5-pro,"
    "gemini-1.5-flash-8b,"
)


def list_model_candidates() -> List[str]:
    raw = os.getenv("GOOGLE_MODEL_CANDIDATES", _DEFAULT_CANDIDATES)
    return [m.strip() for m in raw.split(",") if m.strip()]


def _is_model_unavailable_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    if "404" in str(exc):
        return True
    if "not found" in msg and "model" in msg:
        return True
    if "not supported" in msg and "generatecontent" in msg.replace(" ", ""):
        return True
    if "is not found for api version" in msg:
        return True
    return False


def _is_quota_or_rate_limit_error(exc: BaseException) -> bool:
    raw = str(exc)
    msg = raw.lower()
    if "429" in raw:
        return True
    if "resource exhausted" in msg:
        return True
    if "too many requests" in msg:
        return True
    if "rate limit" in msg:
        return True
    if "quota" in msg:
        return True
    if "exceeded your current quota" in msg:
        return True
    return False


def _parse_retry_seconds(exc: BaseException) -> Optional[float]:
    m = re.search(r"retry in ([0-9.]+)\s*s(?:econds)?", str(exc), re.IGNORECASE)
    if not m:
        return None
    return min(float(m.group(1)), 120.0)


def generate_content_with_fallback(prompt: str) -> Tuple[Any, str]:
    """
    Call Gemini generate_content trying each model name until one succeeds.

    Requires google.generativeai configured (genai.configure) by the caller.

    Returns:
        (response, model_name_used)

    Raises:
        The last error if every candidate fails.
    """
    import google.generativeai as genai

    last_error: BaseException | None = None
    candidates = list_model_candidates()
    if not candidates:
        raise RuntimeError("GOOGLE_MODEL_CANDIDATES is empty")

    # So lan cho "retry in Xs" tren cung mot model (quota theo phut); mac dinh 1. Dat 0 de nhay model ngay.
    max_wait_retries = max(0, int(os.getenv("GEMINI_QUOTA_SLEEP_RETRIES", "1")))

    for name in candidates:
        attempt = 0
        while True:
            try:
                m = genai.GenerativeModel(name)
                response = m.generate_content(prompt)
                print(f"[Gemini] OK with model: {name}")
                return response, name
            except BaseException as e:
                last_error = e
                if _is_model_unavailable_error(e):
                    print(f"[Gemini] Skip model {name} (unavailable): {e!s}"[:220])
                    break

                if _is_quota_or_rate_limit_error(e):
                    wait_s = _parse_retry_seconds(e)
                    if wait_s is not None and attempt < max_wait_retries:
                        print(
                            f"[Gemini] Model {name}: quota/rate limit, cho {wait_s:.1f}s "
                            f"(lan thu {attempt + 1}/{max_wait_retries})..."
                        )
                        time.sleep(wait_s)
                        attempt += 1
                        continue
                    print(
                        f"[Gemini] Skip model {name} (quota/rate limit — thu model tiep theo). "
                        f"{e!s}"[:200]
                    )
                    break

                raise

    assert last_error is not None
    tried = ", ".join(candidates)
    raise RuntimeError(
        f"Khong goi duoc Gemini: da thu {tried}. "
        f"Loi cuoi: {last_error}. "
        "Goi y: (1) Free tier co han theo model/ngay — them nhieu ten model vao GOOGLE_MODEL_CANDIDATES; "
        "(2) dat GEMINI_DISABLE_REQUIREMENT_LLM=1 de bot 1 lan goi API moi bai; "
        "(3) nang cap billing tai Google AI Studio / kiem tra quota."
    ) from last_error
