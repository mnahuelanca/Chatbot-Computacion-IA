# Instalar requests si no lo tenemos -> !pip install requests

import json
import requests
import re

# Cargar el archivo JSON
ruta_archivo = 'data.json'

with open(ruta_archivo, 'r', encoding='utf-8') as f:
    corpus = json.load(f)

datos_qa = corpus['data'] # Accedemos a la lista de diccionarios
print(f"Se cargaron {len(datos_qa)} preguntas y respuestas.")

def buscar_contexto(pregunta_usuario, datos):
    # Limpiamos y separamos la pregunta en palabras clave
    palabras_usuario = set(re.findall(r'\w+', pregunta_usuario.lower()))
    
    mejor_coincidencia = None
    max_score = 0
    
    for item in datos:
        score = 0
        
        # 1. Chequear coincidencia con las keywords del JSON
        keywords_json = set([kw.lower() for kw in item['keywords']])
        if palabras_usuario.intersection(keywords_json):
            score += 5  # Le damos mucho peso a las keywords exactas
            
        # 2. Chequear coincidencia con la pregunta original del JSON
        palabras_pregunta_json = set(re.findall(r'\w+', item['pregunta'].lower()))
        score += len(palabras_usuario.intersection(palabras_pregunta_json))
        
        # Guardar el item con el score más alto
        if score > max_score:
            max_score = score
            mejor_coincidencia = item
            
    # Si encontramos algo con sentido, devolvemos la respuesta del JSON como contexto
    if mejor_coincidencia and max_score > 0:
        return mejor_coincidencia['respuesta']
    
    return "No encontré información sobre este tema en la base de datos."


def chatear_con_llama(pregunta_usuario, contexto):
    url = "http://127.0.0.1:11434/api/generate"
    
    # Armamos un prompt sistémico para que LLaMA sepa cómo comportarse
    prompt = f"""
    Sos un asistente virtual universitario útil y directo.
    Puedes saludar al usuario, pero no te extiendas en eso.
    Si te saluda, no respondas con un saludo largo, solo un "Hola, ¿en qué puedo ayudarte?".
    Usá ÚNICAMENTE la siguiente información para responder a la pregunta del usuario.
    Nunca inventes información ni respondas con algo que no esté en el contexto.
    Tampoco adules al usuario ni te extiendas en saludos o despedidas.
    Si la información proporcionada dice que no hay datos, decile al usuario amablemente que no tenés esa información.
    Si el usuario se despide, respondé con un "¡Hasta luego!".
    
    Información: {contexto}
    
    Pregunta del usuario: {pregunta_usuario}
    """
    
    payload = {
        "model": "llama3", # el nombre debe coincidir con el modelo que tenemos en local
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.RequestException as e:
        return f"Error al conectar con LLaMA 3: {e}"
    

print("¡Chatbot iniciado! Escribí 'salir' para terminar.\n")

while True:
    usuario_input = input("Vos: ")
    
    if usuario_input.lower() in ['salir', 'exit', 'quit']:
        print("Chat finalizado.")
        break
        
    # 1. Buscamos la info en el JSON
    contexto_recuperado = buscar_contexto(usuario_input, datos_qa)
    
    # 2. Generamos la respuesta con LLaMA 3
    respuesta_ia = chatear_con_llama(usuario_input, contexto_recuperado)
    
    print(f"Bot: {respuesta_ia}\n")