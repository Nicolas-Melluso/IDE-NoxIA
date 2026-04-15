# text-generation-studio

Proyecto practico de la Leccion 6: construccion de aplicaciones de generacion de texto.

## Que hace

Convierte prompts en una app usable por menu, con 4 casos reales:

- Generador de recetas
- Resumidor de texto
- Generador de quiz
- Reescritura por tono

Ademas guarda historial con metricas para que puedas comparar costo y rendimiento.

## Estructura

- src/config.py: carga de entorno y parametros
- src/client.py: cliente GitHub Models con retry y backoff
- src/templates.py: plantillas de prompts por caso de uso
- src/history.py: guardado de historial en CSV
- src/main.py: app de consola principal
- results/history.csv: historial de ejecuciones

## Setup

```bash
cd '/c/Users/nicol/OneDrive/Documentos/Projects/ai-learning/text-generation-studio'
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
MAX_RETRIES=4
BASE_DELAY_SECONDS=0.5
```

## Ejecutar

```bash
python src/main.py
```

## Que aprendes aqui (Leccion 6)

- Como convertir prompts en una app real (no solo pruebas sueltas)
- Como ajustar temperatura y max_tokens para cambiar resultados
- Como estructurar prompts por caso de uso
- Como instrumentar una app de texto con metricas y trazabilidad

## Siguiente paso sugerido

Agregar una SPA para visualizar `results/history.csv` con graficos de latencia, tokens y uso por modo.
