import re
import time
import requests


API_URL = "https://models.inference.ai.azure.com/chat/completions"


class APIClient:
    def __init__(self, token: str, max_retries: int = 4, base_delay_seconds: float = 0.5):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.max_retries = max_retries
        self.base_delay_seconds = base_delay_seconds

    def _retry_wait(self, response: requests.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After", "").strip()
        if retry_after:
            try:
                return max(float(retry_after), self.base_delay_seconds)
            except ValueError:
                pass

        match = re.search(r"wait\s+(\d+)\s+seconds", response.text[:500], flags=re.IGNORECASE)
        if match:
            return max(float(match.group(1)), self.base_delay_seconds)

        return self.base_delay_seconds * (2 ** attempt)

    def _post_messages(self, payload: dict) -> dict:
        total_start = time.perf_counter()
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(API_URL, headers=self.headers, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    usage = data.get("usage", {})
                    answer = data["choices"][0]["message"]["content"]
                    return {
                        "ok": True,
                        "status_code": 200,
                        "latency_ms": round((time.perf_counter() - total_start) * 1000, 2),
                        "answer": answer,
                        "prompt_tokens": usage.get("prompt_tokens"),
                        "completion_tokens": usage.get("completion_tokens"),
                        "total_tokens": usage.get("total_tokens"),
                    }

                if response.status_code == 429 and attempt < self.max_retries:
                    time.sleep(self._retry_wait(response, attempt))
                    continue

                return {
                    "ok": False,
                    "status_code": response.status_code,
                    "latency_ms": round((time.perf_counter() - total_start) * 1000, 2),
                    "answer": response.text[:600],
                }
            except Exception as exc:
                if attempt < self.max_retries:
                    time.sleep(self.base_delay_seconds * (2 ** attempt))
                    continue
                return {
                    "ok": False,
                    "status_code": -1,
                    "latency_ms": round((time.perf_counter() - total_start) * 1000, 2),
                    "answer": str(exc)[:600],
                }

    def chat(self, model: str, messages: list[dict], temperature: float, max_tokens: int) -> dict:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        return self._post_messages(payload)

    def generate(self, model: str, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> dict:
        return self.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
