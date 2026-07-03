import json
import unicodedata
import os
import sys
import difflib

try:
    from flask import Flask, request, jsonify, render_template
except Exception:
    Flask = None

# 1. Cargar los datos
def cargar_datos(archivo):
    ruta = os.path.join(os.path.dirname(__file__), archivo)
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['data']

# 2. Función para normalizar texto
def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto

# 3. Lógica del modelo NLU (Comprensión del lenguaje natural)
def obtener_respuesta(user_input, base_datos):
    input_limpio = normalizar(user_input)
    # Scoring
    best_item = None
    best_score = 0

    for item in base_datos:
        keywords_lista = [normalizar(kw) for kw in item['keywords']]
        score = 0
        for kw in keywords_lista:
            if kw and kw in input_limpio:
                score += 1
        if score > best_score:
            best_score = score
            best_item = item

    if best_score > 0 and best_item:
        return best_item['respuesta']

    # Buscar la pregunta más parecida por similitud de texto
    preguntas = [normalizar(item['pregunta']) for item in base_datos]
    matches = difflib.get_close_matches(input_limpio, preguntas, n=1, cutoff=0.6)
    if matches:
        match = matches[0]
        for item in base_datos:
            if normalizar(item['pregunta']) == match:
                return item['respuesta']

    return "Lo siento, no tengo información sobre eso."

# --- Ejecución ---
app = None
datos = cargar_datos('data.json')

if Flask:
    app = Flask(__name__, static_folder='static', template_folder='templates')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/chat', methods=['POST'])
    def chat():
        payload = request.get_json(force=True)
        message = payload.get('message', '')
        respuesta = obtener_respuesta(message, datos)
        return jsonify({'response': respuesta})

    @app.route('/smoke', methods=['GET'])
    def smoke_summary():
        hits = 0
        failures = []
        for item in datos:
            pregunta = item.get('pregunta', '')
            respuesta_esperada = item.get('respuesta', '')
            respuesta_obtenida = obtener_respuesta(pregunta, datos)
            if respuesta_obtenida == respuesta_esperada:
                hits += 1
            else:
                failures.append({
                    'id': item.get('id'),
                    'pregunta': pregunta,
                    'esperado': respuesta_esperada,
                    'obtenido': respuesta_obtenida
                })
        total = len(datos)
        score = round(hits / total * 100, 2) if total else 0.0
        return jsonify({
            'total': total,
            'hits': hits,
            'errors': len(failures),
            'score': score,
            'failures': failures
        })

if __name__ == "__main__":
    # CLI por defecto; si se pasa '--serve', arranca el servidor web (requiere Flask)
    if '--serve' in sys.argv:
        if not Flask:
            print("Flask no está instalado. Instale 'flask' para usar el servidor web.")
            sys.exit(1)
        print('Iniciando servidor en http://127.0.0.1:5000 ...')
        app.run(debug=True, port=5000)
    else:
        print("¡Hola! Soy el asistente de TechSolutions. (Escribe 'salir' para terminar)")
        while True:
            usuario = input("\n¿Qué deseas saber?: ")
            if usuario.lower() == 'salir':
                break
            respuesta = obtener_respuesta(usuario, datos)
            print(f"Bot: {respuesta}")