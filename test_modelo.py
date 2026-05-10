import json
import time
from modeloCL import buscar_contexto, chatear_con_llama

# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────

ruta_archivo = 'data.json'
with open(ruta_archivo, 'r', encoding='utf-8') as f:
    corpus = json.load(f)

datos_qa = corpus['data']

# ─────────────────────────────────────────────
# CONFIGURACIÓN DEL TEST
# ─────────────────────────────────────────────

LOTE = 50  # Cuántos ítems testear
lote_prueba = datos_qa[:LOTE]
resultados_test = []
aciertos_buscador = 0

print(f"Iniciando smoke test con los primeros {LOTE} ítems...\n")

for i, item in enumerate(lote_prueba):
    pregunta_test    = item['pregunta']
    respuesta_esperada = item['respuesta']

    # buscar_contexto devuelve una LISTA de strings
    contextos = buscar_contexto(pregunta_test, datos_qa)

    hit = respuesta_esperada in contextos

    if hit:
        aciertos_buscador += 1

    # Llamamos a LLaMA solo si el buscador encontró algo
    if contextos:
        respuesta_ia = chatear_con_llama(pregunta_test, contextos)
    else:
        respuesta_ia = "No tengo esa información."

    resultados_test.append({
        "id":               item.get("id", i + 1),
        "pregunta":         pregunta_test,
        "respuesta_esperada": respuesta_esperada,
        "contextos_encontrados": contextos,
        "hit_buscador":    hit,
        "respuesta_ia":    respuesta_ia
    })

    print(f"  [{i+1:>2}/{LOTE}] hit={hit} | pregunta: {pregunta_test[:50]}")

    # Sin sleep extra: LLaMA ya tiene su propia latencia.
    # rate-limits en algún servicio externo:
    # time.sleep(0.2)

# ─────────────────────────────────────────────
# MÉTRICAS FINALES
# ─────────────────────────────────────────────

efectividad = (aciertos_buscador / LOTE) * 100
print(f"\n{'='*50}")
print(f"Efectividad del Buscador: {efectividad:.1f}%  ({aciertos_buscador}/{LOTE} aciertos)")
print(f"{'='*50}\n")

# ─────────────────────────────────────────────
# GUARDAR RESULTADOS
# ─────────────────────────────────────────────

output_path = 'resultados_test.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(resultados_test, f, ensure_ascii=False, indent=4)

print(f"Resultados guardados en '{output_path}'.")
