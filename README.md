# IDE NoxIA

Construyendo un IDE web

## Que hace

- Modo web: un editor tipo IDE a la izquierda y un chat LLM a la derecha.

En la interfaz web, el usuario escribe codigo o texto en el editor y luego conversa con la IA para pedir explicaciones, refactors, mejoras o reescrituras usando ese contenido como contexto.

Ademas guarda historial con metricas para comparar costo y rendimiento.

## Estructura

- src/config.py: carga de entorno y parametros
- src/client.py: cliente GitHub Models con retry, backoff y soporte chat
- src/server.py: servidor web local + API `/api/chat`
- src/cli.py: flujo legado de consola
- src/templates.py: plantillas de prompts por caso de uso
- src/history.py: guardado de historial en CSV para consola y chat
- src/main.py: arranque principal (web por defecto, CLI opcional)
- web/: SPA tipo editor + chat
- results/history.csv: historial de ejecuciones
- results/chat_history.csv: historial de conversaciones web

## Setup

```bash
cd 'IDE-NoxIA'
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env`:

```env
GITHUB_TOKEN=github_pat_xxxxxxxxxxxxx
MODEL=gpt-4o-mini
TEMPERATURE=0.4
MAX_TOKENS=350
MAX_RETRIES=3
BASE_DELAY_SECONDS=0.5
PORT=8000
```

## Ejecutar producto web

```bash
python src/main.py
```

Abre luego:

```text
http://127.0.0.1:8000
```

## Ejecutar modo consola

```bash
python src/main.py --cli
```