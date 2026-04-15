import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from client import APIClient
from config import Config
from history import append_chat_history


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = PROJECT_ROOT / "web"
RESULTS_DIR = PROJECT_ROOT / "results"


def build_messages(editor_content: str, conversation: list[dict], user_message: str) -> list[dict]:
    editor_excerpt = editor_content.strip()
    if len(editor_excerpt) > 8000:
        editor_excerpt = editor_excerpt[:8000]

    system_prompt = (
        "Eres un asistente de codigo y escritura integrado en un editor tipo IDE. "
        "Ayuda al usuario a entender, corregir, reescribir y continuar el contenido que tiene abierto. "
        "Si el contenido es codigo, explica con precision tecnica y propone cambios concretos. "
        "Si el contenido es texto, ayuda con estructura, claridad y reescritura. "
        "Responde en espanol, con claridad, y prioriza acciones utiles sobre teoria."
    )

    context_message = {
        "role": "system",
        "content": (
            "Contenido actual del editor del usuario. Usa este contexto para responder. "
            "Si el usuario pregunta por algo fuera del editor, puedes responder igual, pero prioriza el documento abierto.\n\n"
            f"--- INICIO DEL EDITOR ---\n{editor_excerpt or '[Editor vacio]'}\n--- FIN DEL EDITOR ---"
        ),
    }

    recent_history = []
    for item in conversation[-10:]:
        role = item.get("role")
        content = item.get("content", "")
        if role in {"user", "assistant"} and content:
            recent_history.append({"role": role, "content": content})

    return [
        {"role": "system", "content": system_prompt},
        context_message,
        *recent_history,
        {"role": "user", "content": user_message},
    ]


class AppHandler(BaseHTTPRequestHandler):
    config = Config()
    client = APIClient(
        token=config.token,
        max_retries=config.max_retries,
        base_delay_seconds=config.base_delay_seconds,
    )

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self._send_json(200, {"ok": True, "model": self.config.model})
            return

        if path == "/":
            path = "/index.html"

        self._serve_static(path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/chat":
            self._send_json(404, {"error": "Not found"})
            return

        body = self._read_json_body()
        if body is None:
            self._send_json(400, {"error": "JSON invalido"})
            return

        user_message = str(body.get("message", "")).strip()
        editor_content = str(body.get("editorContent", ""))
        conversation = body.get("conversation") or []
        session_id = str(body.get("sessionId") or uuid4())

        if not user_message:
            self._send_json(400, {"error": "Falta message"})
            return

        messages = build_messages(editor_content, conversation, user_message)
        result = self.client.chat(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        append_chat_history(
            {
                "session_id": session_id,
                "model": self.config.model,
                "status_code": result.get("status_code"),
                "latency_ms": result.get("latency_ms"),
                "prompt_tokens": result.get("prompt_tokens"),
                "completion_tokens": result.get("completion_tokens"),
                "total_tokens": result.get("total_tokens"),
                "editor_excerpt": editor_content,
                "user_message": user_message,
                "assistant_preview": (result.get("answer") or "").replace("\n", " "),
            },
            RESULTS_DIR / "chat_history.csv",
        )

        self._send_json(
            200,
            {
                "ok": result.get("ok"),
                "answer": result.get("answer"),
                "status_code": result.get("status_code"),
                "latency_ms": result.get("latency_ms"),
                "prompt_tokens": result.get("prompt_tokens"),
                "completion_tokens": result.get("completion_tokens"),
                "total_tokens": result.get("total_tokens"),
                "sessionId": session_id,
            },
        )

    def _serve_static(self, path: str) -> None:
        relative = path.lstrip("/")
        file_path = (WEB_ROOT / relative).resolve()
        if WEB_ROOT not in file_path.parents and file_path != WEB_ROOT:
            self._send_json(403, {"error": "Forbidden"})
            return
        if not file_path.exists() or not file_path.is_file():
            self._send_json(404, {"error": "Archivo no encontrado"})
            return

        content_type, _ = mimetypes.guess_type(str(file_path))
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return None

    def _send_json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:
        return


def run_server() -> None:
    config = Config()
    server = ThreadingHTTPServer(("127.0.0.1", config.port), AppHandler)
    print(f"Text Generation Studio Web en http://127.0.0.1:{config.port}")
    print("Usa python src/main.py --cli para el modo consola.")
    server.serve_forever()
