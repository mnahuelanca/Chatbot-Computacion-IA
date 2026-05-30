import json
import unicodedata
from app import obtener_respuesta, datos

def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto

def run_smoke():
    total = len(datos)
    aciertos = 0
    detalles = []

    for item in datos:
        entrada = item['pregunta']
        esperado = normalizar(item['respuesta'])
        obtenido = normalizar(obtener_respuesta(entrada, datos))

        ok = (obtenido == esperado)
        if ok:
            aciertos += 1
        else:
            detalles.append({
                'id': item['id'],
                'pregunta': item['pregunta'],
                'esperado': item['respuesta'],
                'obtenido': obtenido
            })

    porcentaje = aciertos / total * 100 if total else 0
    resultado = {
        'total': total,
        'aciertos': aciertos,
        'errores': total - aciertos,
        'porcentaje': porcentaje,
        'detalles': detalles
    }

    with open('resultados_smoketest.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"Total: {total}, Aciertos: {aciertos}, Errores: {total-aciertos}, Porcentaje: {porcentaje:.1f}%")
    print("Detalles guardados en resultados_smoketest.json")

if __name__ == '__main__':
    run_smoke()
