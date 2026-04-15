GENERATION_MODES = {
    "1": {
        "name": "Generador de recetas",
        "system": "Eres un chef practico. Responde en espanol claro y accionable.",
        "builder": lambda user_input: (
            "Crea 3 recetas con estos ingredientes y agrega pasos claros, tiempo estimado "
            f"y consejos de preparacion: {user_input}"
        ),
    },
    "2": {
        "name": "Resumidor de texto",
        "system": "Eres un asistente academico. Resume con precision y claridad.",
        "builder": lambda user_input: (
            "Resume el siguiente texto en: 1) 5 bullets, 2) resumen de 3 lineas, "
            f"3) 2 preguntas de repaso. Texto: {user_input}"
        ),
    },
    "3": {
        "name": "Generador de quiz",
        "system": "Eres un creador de evaluaciones didacticas.",
        "builder": lambda user_input: (
            "Genera un quiz de 5 preguntas de opcion multiple con respuesta correcta y explicacion "
            f"sobre este tema: {user_input}"
        ),
    },
    "4": {
        "name": "Reescritura por tono",
        "system": "Eres un editor de estilo profesional.",
        "builder": lambda user_input: (
            "Reescribe este texto en 3 tonos: formal, amigable y tecnico. "
            f"Texto original: {user_input}"
        ),
    },
}
