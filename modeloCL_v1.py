import json
import requests
import re
import unicodedata

# ─────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────

def normalizar(texto):
    """
    Pasa a minúsculas y elimina tildes/diacríticos.
    'computación' → 'computacion', 'ñ' → 'n', etc.
    Esto es clave para que el matching de keywords funcione
    aunque el usuario escriba con o sin tildes.
    """
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto

def tokenizar(texto):
    """Devuelve un set de palabras normalizadas."""
    return set(re.findall(r'\w+', normalizar(texto)))


# ─────────────────────────────────────────────
# CARGA DE DATOS (una sola vez)
# ─────────────────────────────────────────────

with open("data.json", "r", encoding="utf-8") as f:
    _data_completa = json.load(f)

corpus = _data_completa["data"]
print(f"Se cargaron {len(corpus)} preguntas y respuestas.")


# ─────────────────────────────────────────────
# BUSCADOR
# ─────────────────────────────────────────────

def buscar_contexto(pregunta_usuario, datos, top_k=2):
    """
    Busca los contextos más relevantes para la pregunta del usuario.
    Devuelve una lista de strings (las respuestas del top_k más parecidos).
    """
    palabras_usuario = tokenizar(pregunta_usuario)

    resultados = []

    for item in datos:
        score = 0

        # 1. Coincidencia con keywords del JSON (normalizadas)
        keywords_json = set(normalizar(kw) for kw in item['keywords'])
        coincidencias_kw = palabras_usuario.intersection(keywords_json)
        score += len(coincidencias_kw) * 5  # Peso alto a keywords exactas

        # 2. Coincidencia con las palabras de la pregunta original del JSON
        palabras_pregunta_json = tokenizar(item['pregunta'])
        score += len(palabras_usuario.intersection(palabras_pregunta_json))

        if score > 0:
            resultados.append((score, item['respuesta']))

    resultados.sort(reverse=True, key=lambda x: x[0])

    return [texto for _, texto in resultados[:top_k]]


# ─────────────────────────────────────────────
# LLAMADA A LLAMA (vía Ollama local)
# ─────────────────────────────────────────────

def chatear_con_llama(pregunta_usuario, contexto):
    """
    Llama al modelo LLaMA 3 corriendo en Ollama local.
    El contexto puede ser un string o una lista de strings.
    """
    # Si contexto llega como lista, lo unimos
    if isinstance(contexto, list):
        contexto = "\n".join(contexto)

    url = "http://127.0.0.1:11434/api/generate"

    # Sin indentación extra dentro del f-string para no mandar basura al modelo
    prompt = (
        "Sos un asistente virtual universitario estricto y directo. "
        "Tu única función es devolver la información del Contexto.\n\n"
        "REGLAS ESTRICTAS:\n"
        "1. PROHIBIDO saludar, presentarte o despedirte. Ve directamente a la respuesta.\n"
        "2. Responde ÚNICAMENTE usando la información provista en el Contexto. "
        "No agregues explicaciones, ejemplos ni relleno.\n"
        "3. PROHIBIDO agregar información de tus propios conocimientos.\n"
        "4. Si la respuesta a la Pregunta no está en el Contexto, "
        'responde exactamente: "No tengo esa información."\n\n'
        f"Contexto:\n{contexto}\n\n"
        f"Pregunta del usuario: {pregunta_usuario}"
    )

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.ConnectionError:
        return "Error: no se pudo conectar con Ollama. ¿Está corriendo en el puerto 11434?"
    except requests.exceptions.Timeout:
        return "Error: LLaMA tardó demasiado en responder."
    except requests.exceptions.RequestException as e:
        return f"Error al conectar con LLaMA 3: {e}"


# ─────────────────────────────────────────────
# FUNCIÓN PRINCIPAL DEL CHAT
# ─────────────────────────────────────────────

def chat(pregunta_usuario):
    """
    Punto de entrada principal. Filtra saludos/despedidas,
    busca contexto en el JSON y llama a LLaMA solo si es necesario.
    """
    pregunta_limpia = normalizar(pregunta_usuario).strip()

    # Atajos rápidos: saludos y despedidas (normalizados, sin tildes)
    saludos = {"hola", "buenas", "buen dia", "buenas tardes", "buenas noches", "hey"}
    despedidas = {"chau", "adios", "hasta luego", "nos vemos"}

    if pregunta_limpia in saludos:
        return "¡Hola! ¿En qué te puedo ayudar?"

    if pregunta_limpia in despedidas:
        return "¡Hasta luego!"

    # Buscar contexto relevante en el corpus
    contextos = buscar_contexto(pregunta_usuario, corpus)

    if not contextos:
        return "No tengo esa información."

    # Llamar a LLaMA con el contexto encontrado
    respuesta = chatear_con_llama(pregunta_usuario, contextos)
    return respuesta.strip()


# ─────────────────────────────────────────────
# EJECUCIÓN DIRECTA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("¡Chatbot iniciado! Escribí 'salir' para terminar.\n")

    while True:
        usuario_input = input("Vos: ").strip()

        if not usuario_input:
            continue

        if usuario_input.lower() in {'salir', 'exit', 'quit'}:
            print("Bot: ¡Hasta luego! Chat finalizado.")
            break

        respuesta = chat(usuario_input)
        print(f"Bot: {respuesta}\n")
