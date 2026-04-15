from pathlib import Path

from client import APIClient
from config import Config
from history import append_history
from templates import GENERATION_MODES


def show_menu() -> None:
    print("\n" + "=" * 62)
    print("Text Generation Studio")
    print("=" * 62)
    for key, mode in GENERATION_MODES.items():
        print(f"{key}. {mode['name']}")
    print("0. Salir")


def run() -> None:
    config = Config()
    client = APIClient(
        token=config.token,
        max_retries=config.max_retries,
        base_delay_seconds=config.base_delay_seconds,
    )
    history_file = Path("results") / "history.csv"

    while True:
        show_menu()
        choice = input("\nElige una opcion: ").strip()
        if choice == "0":
            print("Hasta luego.")
            return

        if choice not in GENERATION_MODES:
            print("Opcion invalida. Intenta de nuevo.")
            continue

        mode = GENERATION_MODES[choice]
        user_input = input(f"\nEntrada para '{mode['name']}': ").strip()
        if not user_input:
            print("Entrada vacia, intenta otra vez.")
            continue

        user_prompt = mode["builder"](user_input)
        result = client.generate(
            model=config.model,
            system_prompt=mode["system"],
            user_prompt=user_prompt,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

        print("\n" + "-" * 62)
        if result.get("ok"):
            print(result["answer"])
        else:
            print(f"Error [{result.get('status_code')}]: {result.get('answer')}")
        print("-" * 62)

        print(
            "Metricas -> "
            f"status={result.get('status_code')} "
            f"latency={result.get('latency_ms')}ms "
            f"tokens={result.get('total_tokens')}"
        )

        append_history(
            {
                "mode": mode["name"],
                "model": config.model,
                "status_code": result.get("status_code"),
                "latency_ms": result.get("latency_ms"),
                "prompt_tokens": result.get("prompt_tokens"),
                "completion_tokens": result.get("completion_tokens"),
                "total_tokens": result.get("total_tokens"),
                "user_input": user_input,
                "answer_preview": (result.get("answer") or "").replace("\n", " "),
            },
            history_file,
        )


if __name__ == "__main__":
    run()
