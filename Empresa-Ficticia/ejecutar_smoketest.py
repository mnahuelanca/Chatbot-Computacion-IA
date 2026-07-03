import json
import os
import unicodedata
import difflib


def cargar_datos(archivo):
    ruta = os.path.join(os.path.dirname(__file__), archivo)
    with open(ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    return datos.get('data', [])


def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto


def obtener_respuesta(user_input, base_datos):
    input_limpio = normalizar(user_input)
    best_item = None
    best_score = 0

    for item in base_datos:
        keywords_lista = [normalizar(kw) for kw in item.get('keywords', [])]
        score = 0
        for kw in keywords_lista:
            if kw and kw in input_limpio:
                score += 1
        if score > best_score:
            best_score = score
            best_item = item

    if best_score > 0 and best_item:
        return best_item.get('respuesta', '')

    preguntas = [normalizar(item.get('pregunta', '')) for item in base_datos]
    matches = difflib.get_close_matches(input_limpio, preguntas, n=1, cutoff=0.6)
    if matches:
        match = matches[0]
        for item in base_datos:
            if normalizar(item.get('pregunta', '')) == match:
                return item.get('respuesta', '')

    return "Lo siento, no tengo información sobre eso."


def ejecutar_smoketest():
    datos = cargar_datos('data.json')
    total = len(datos)
    hits = 0
    failures = []
    resultados = []

    for item in datos:
        pregunta = item.get('pregunta', '').strip()
        esperado = item.get('respuesta', '')
        obtenido = obtener_respuesta(pregunta, datos)
        correcto = obtenido == esperado

        resultados.append({
            'id': item.get('id'),
            'pregunta': pregunta,
            'esperado': esperado,
            'obtenido': obtenido,
            'correcto': correcto,
        })

        if correcto:
            hits += 1
        else:
            failures.append({
                'id': item.get('id'),
                'pregunta': pregunta,
                'esperado': esperado,
                'obtenido': obtenido,
            })

    score = round((hits / total) * 100, 2) if total else 0.0
    resumen = {
        'total': total,
        'hits': hits,
        'errors': len(failures),
        'score': score,
        'failures': failures,
        'results': resultados,
    }

    ruta_salida = os.path.join(os.path.dirname(__file__), 'resultados_smoketest_v2.json')
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)

    print(f"Smoke test completado: {hits}/{total} aciertos ({score}%).")
    print(f"Archivo guardado en: {ruta_salida}")


if __name__ == '__main__':
    ejecutar_smoketest()
