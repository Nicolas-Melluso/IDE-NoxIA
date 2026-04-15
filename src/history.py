import csv
from datetime import datetime
from pathlib import Path


def append_history(row: dict, file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    exists = file_path.exists()

    fields = [
        "timestamp",
        "mode",
        "model",
        "status_code",
        "latency_ms",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "user_input",
        "answer_preview",
    ]

    with file_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "mode": row.get("mode"),
            "model": row.get("model"),
            "status_code": row.get("status_code"),
            "latency_ms": row.get("latency_ms"),
            "prompt_tokens": row.get("prompt_tokens"),
            "completion_tokens": row.get("completion_tokens"),
            "total_tokens": row.get("total_tokens"),
            "user_input": row.get("user_input", "")[:300],
            "answer_preview": row.get("answer_preview", "")[:300],
        })


def append_chat_history(row: dict, file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    exists = file_path.exists()

    fields = [
        "timestamp",
        "session_id",
        "model",
        "status_code",
        "latency_ms",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "editor_excerpt",
        "user_message",
        "assistant_preview",
    ]

    with file_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "session_id": row.get("session_id"),
            "model": row.get("model"),
            "status_code": row.get("status_code"),
            "latency_ms": row.get("latency_ms"),
            "prompt_tokens": row.get("prompt_tokens"),
            "completion_tokens": row.get("completion_tokens"),
            "total_tokens": row.get("total_tokens"),
            "editor_excerpt": row.get("editor_excerpt", "")[:400],
            "user_message": row.get("user_message", "")[:300],
            "assistant_preview": row.get("assistant_preview", "")[:400],
        })
