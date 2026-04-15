import os
from dotenv import load_dotenv


class Config:
    def __init__(self) -> None:
        load_dotenv()
        self.token = os.getenv("GITHUB_TOKEN", "").strip()
        self.model = os.getenv("MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
        self.temperature = float(os.getenv("TEMPERATURE", "0.4"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "350"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "4"))
        self.base_delay_seconds = float(os.getenv("BASE_DELAY_SECONDS", "0.5"))
        self._validate()

    def _validate(self) -> None:
        if not self.token:
            raise SystemExit("Falta GITHUB_TOKEN en .env")
        if self.token.lower() in {"tu_token", "tu_token_real", "your_token", "token"}:
            raise SystemExit("GITHUB_TOKEN parece placeholder. Usa uno real.")
