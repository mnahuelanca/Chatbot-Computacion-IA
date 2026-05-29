import json
import unicodedata

# 1. Cargar los datos
def cargar_datos(archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['data']  # Accedemos a la lista dentro de la clave 'data'

# 2. Función para normalizar texto (quita tildes y pasa a minúsculas)
def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto

# 3. Lógica del modelo NLU
def obtener_respuesta(user_input, base_datos):
    input_limpio = normalizar(user_input)
    
    for item in base_datos:
        # Normalizamos las keywords del JSON para comparar
        keywords_lista = [normalizar(kw) for kw in item['keywords']]
        
        # Verificamos si alguna palabra clave está en el input del usuario
        if any(kw in input_limpio for kw in keywords_lista):
            return item['respuesta']
            
    return "Lo siento, no tengo información sobre eso."

# --- Ejecución ---
if __name__ == "__main__":
    datos = cargar_datos('data.json')
    
    print("¡Hola! Soy el asistente de TechSolutions. (Escribe 'salir' para terminar)")
    
    while True:
        usuario = input("\n¿Qué deseas saber?: ")
        
        if usuario.lower() == 'salir':
            break
            
        respuesta = obtener_respuesta(usuario, datos)
        print(f"Bot: {respuesta}")