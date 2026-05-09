# Instalar requests si no lo tenemos -> !pip install requests

import json
import requests
import re

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def json_a_texto(data):
    textos = []
    
    for item in data:
        if isinstance(item, dict):
            texto = " ".join([f"{k}: {v}" for k, v in item.items()])
        else:
            texto = str(item)
            
        textos.append(texto)
    
    return textos

corpus = json_a_texto(data)


def buscar_contexto(pregunta, corpus, top_k=3):
    resultados = []
    
    for texto in corpus:
        score = sum(palabra in texto.lower() for palabra in pregunta.lower().split())
        resultados.append((score, texto))
    
    resultados.sort(reverse=True)
    
    return [texto for _, texto in resultados[:top_k]]



def preguntar_llama(pregunta, contexto):
    url = "http://localhost:11434/api/generate"
    
    prompt = f"""
                Sos un asistente virtual universitario útil y directo.
                Puedes saludar al usuario, pero no te extiendas en eso.
                Si te saluda, no respondas con un saludo largo, solo un "Hola, ¿en qué puedo ayudarte?".
                Usá ÚNICAMENTE la siguiente información para responder a la pregunta del usuario.
                Nunca inventes información ni respondas con algo que no esté en el contexto.
                Tampoco adules al usuario ni te extiendas en saludos o despedidas.
                Si la información proporcionada dice que no hay datos, decile al usuario amablemente que no tenés esa información.
                Si no sabes responder, decile al usuario que no tenés esa información.
                Si el usuario se despide, respondé con un "¡Hasta luego!".

                Contexto:
                {contexto}

                Pregunta:
                {pregunta}
                """

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Error: {response.status_code}"
    


def chat(pregunta):
    contextos = buscar_contexto(pregunta, corpus)
    contexto_unido = "\n".join(contextos)
    
    respuesta = preguntar_llama(pregunta, contexto_unido)
    
    return respuesta


while True:
    pregunta = input("Vos: ")
    
    if pregunta.lower() == "salir":
        break
    
    respuesta = chat(pregunta)
    print("Bot:", respuesta)

    # 'salir' para terminar el chat