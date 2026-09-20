"""
Genera una historia de terror inventada junto con una lista de "momentos clave":
puntos del guion donde debe cambiar la imagen, indicando si es el narrador
(Osvaldo) o una escena de la propia historia, con una descripción de esa imagen.

Llama a OmniRoute (gateway propio desplegado en Railway) usando tus propias
cuentas conectadas (Gemini y Mistral), con fallback manual: si Gemini falla,
prueba con Mistral.

Necesita las variables de entorno:
  - OMNIROUTE_BASE_URL (ej: https://tu-proyecto.up.railway.app/v1)
  - OMNIROUTE_API_KEY

Guarda el resultado en historia_generada.json
"""

import os
import json
import re
import time
import urllib.request
import urllib.error

BASE_URL = os.environ.get("OMNIROUTE_BASE_URL", "").rstrip("/")
API_KEY = os.environ.get("OMNIROUTE_API_KEY")
MODELOS = ["gemini/gemini-3.7-flash", "mistral/mistral-medium-3.5"]

if not BASE_URL:
    raise SystemExit("Falta la variable de entorno OMNIROUTE_BASE_URL")
if not API_KEY:
    raise SystemExit("Falta la variable de entorno OMNIROUTE_API_KEY")

URL = f"{BASE_URL}/chat/completions"

PROMPT = """
Eres el guionista del canal de YouTube de terror "Cuentos de Osvaldo".
El narrador es Osvaldo: un anciano contador de historias, siniestro y con humor negro,
de pelo blanco despeinado, gorra marrón, ojos claros casi blancos, sonrisa torcida,
chaqueta marrón remendada, chaleco verde, pañuelo al cuello.

Tarea:
1. Escribe una historia de terror ORIGINAL e INVENTADA (no un relato conocido),
   pensada para ser narrada en voz alta durante unos 18-20 minutos (aprox 2500-3000 palabras).
   Debe tener tono siniestro con toques de humor negro, propio de Osvaldo.
   El terror debe apoyarse en suspense, atmósfera y sugerencia, evitando
   descripciones explícitas y gráficas de violencia extrema, sangre o mutilación.
2. Divide esa narración en fragmentos de forma natural (por escenas o giros de la historia).
3. Para cada fragmento, decide qué imagen debe mostrarse mientras se narra:
   - tipo "narrador": Osvaldo contando esa parte, en un lugar y con una expresión
     acorde al momento de la historia. El lugar y la expresión deben variar entre
     fragmentos, no repetir siempre el mismo.
   - tipo "escena": una ilustración de lo que ocurre en la historia en ese momento
     (el monstruo, el lugar, el personaje, el objeto siniestro, etc.), sin que
     aparezca Osvaldo.

Responde ÚNICAMENTE con un JSON válido, sin texto adicional ni marcado de código,
con esta forma exacta:

{
  "titulo": "string",
  "fragmentos": [
    {
      "texto": "fragmento del guion a narrar",
      "tipo": "narrador" o "escena",
      "prompt_imagen": "descripción detallada en español para generar la imagen, coherente con el estilo: ilustración plana, líneas negras definidas, colores apagados (marrones, verdes, grises oscuros), sin sombreado realista"
    }
  ]
}
"""


def pedir_historia(modelo):
    body = {
        "model": modelo,
        "messages": [{"role": "user", "content": PROMPT}],
        "response_format": {"type": "json_object"},
        "max_tokens": 8000,
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("ERROR de OmniRoute:")
        print(e.read().decode("utf-8"))
        return None

    try:
        texto = data["choices"][0]["message"]["content"]
        modelo_usado = data.get("model", "?")
        print(f"  (respondió el modelo: {modelo_usado})")
    except (KeyError, IndexError):
        print("Respuesta inesperada de OmniRoute, contenido completo:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return None

    texto_limpio = re.sub(r"^```json\s*|\s*```$", "", texto.strip())
    try:
        return json.loads(texto_limpio, strict=False)
    except json.JSONDecodeError as e:
        print(f"JSON inválido ({e})")
        return None


def main():
    historia = None
    for intento in range(1, 5 + 1):
        modelo = MODELOS[(intento - 1) % len(MODELOS)]
        print(f"Intento {intento} de generar la historia (modelo: {modelo})...")
        historia = pedir_historia(modelo)
        if historia and "fragmentos" in historia and historia["fragmentos"]:
            break
        historia = None
        time.sleep(5)

    if not historia:
        raise SystemExit("No se pudo generar una historia válida tras varios intentos")

    with open("historia_generada.json", "w", encoding="utf-8") as f:
        json.dump(historia, f, ensure_ascii=False, indent=2)

    print(f"Historia generada: {historia['titulo']}")
    print(f"Fragmentos: {len(historia['fragmentos'])}")


if __name__ == "__main__":
    main()
