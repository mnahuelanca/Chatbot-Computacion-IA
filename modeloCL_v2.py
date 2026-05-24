import json
import requests
import re

# ─────────────────────────────────────────────
# CARGA DEL JSON
# ─────────────────────────────────────────────

with open("data.json", "r", encoding="utf-8") as f:
    _data_completa = json.load(f)

corpus = _data_completa["data"]

print(f"Se cargaron {len(corpus)} preguntas y respuestas.")

# ─────────────────────────────────────────────
# GENERAR CATÁLOGO DE PREGUNTAS
# ─────────────────────────────────────────────

catalogo_preguntas = "\n".join(
    f'{item["id"]}: {item["pregunta"]}'
    for item in corpus
)

# ─────────────────────────────────────────────
# CONSULTAR LLAMA PARA OBTENER ID
# ─────────────────────────────────────────────

def obtener_id_con_llama(pregunta_usuario):

    url = "http://127.0.0.1:11434/api/generate"

    prompt = f"""
Sos un clasificador de preguntas.

Tu única tarea es determinar cuál pregunta del catálogo
coincide mejor con la consulta del usuario.

REGLAS OBLIGATORIAS:

- Respondé únicamente el número ID.
- No expliques.
- No escribas texto adicional.
- No uses comillas.
- No uses puntuación.
- Si ninguna pregunta coincide, respondé exactamente:

NO_ENCONTRADA

CATÁLOGO:

{catalogo_preguntas}

CONSULTA DEL USUARIO:

{pregunta_usuario}
"""

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        respuesta = response.json()["response"].strip()

        return respuesta

    except requests.exceptions.ConnectionError:
        return None

    except requests.exceptions.Timeout:
        return None

    except requests.exceptions.RequestException:
        return None


# ─────────────────────────────────────────────
# BUSCAR RESPUESTA POR ID
# ─────────────────────────────────────────────

def buscar_respuesta_por_id(id_pregunta):

    for item in corpus:

        if item["id"] == id_pregunta:
            return item["respuesta"]

    return None


# ─────────────────────────────────────────────
# CHAT PRINCIPAL
# ─────────────────────────────────────────────

def chat(pregunta_usuario):

    resultado_llama = obtener_id_con_llama(
        pregunta_usuario
    )

    if resultado_llama is None:
        return "Error al conectar con LLaMA."

    if resultado_llama == "NO_ENCONTRADA":
        return "No tengo información sobre esa pregunta."

    try:

        id_encontrado = int(
            re.findall(r"\d+", resultado_llama)[0]
        )

    except:
        return "No tengo información sobre esa pregunta."

    respuesta = buscar_respuesta_por_id(
        id_encontrado
    )

    if respuesta:
        return respuesta

    return "No tengo información sobre esa pregunta."


# ─────────────────────────────────────────────
# PRUEBA LOCAL
# ─────────────────────────────────────────────

if __name__ == "__main__":

    print("Chat iniciado.\n")

    while True:

        pregunta = input("Vos: ")

        if pregunta.lower() in {
            "salir",
            "exit",
            "quit"
        }:
            break

        respuesta = chat(pregunta)

        print(f"\nBot: {respuesta}\n")