"""
Genera una historia de terror inventada junto con una lista de "momentos clave":
puntos del guion donde debe cambiar la imagen, indicando si es el narrador
(Osvaldo) o una escena de la propia historia, con una descripción de esa imagen.

Necesita una variable de entorno GEMINI_API_KEY (clave gratuita de Google AI Studio).
Guarda el resultado en historia_generada.json
"""

import os
import json
import re
import urllib.request
import urllib.error

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit("Falta la variable de entorno GEMINI_API_KEY")

MODEL = "gemini-2.0-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

PROMPT = """
Eres el guionista del canal de YouTube de terror "Cuentos de Osvaldo".
El narrador es Osvaldo: un anciano contador de historias, siniestro y con humor negro,
de pelo blanco despeinado, gorra marrón, ojos claros casi blancos, sonrisa torcida,
chaqueta marrón remendada, chaleco verde, pañuelo al cuello.

Tarea:
1. Escribe una historia de terror ORIGINAL e INVENTADA (no un relato conocido),
   pensada para ser narrada en voz alta durante unos 18-20 minutos (aprox 2500-3000 palabras).
   Debe tener tono siniestro con toques de humor negro, propio de Osvaldo.
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


def main():
    body = {
        "contents": [{"parts": [{"text": PROMPT}]}],
        "generationConfig": {"temperature": 1.0, "maxOutputTokens": 8192},
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("ERROR de la API de Gemini:")
        print(e.read().decode("utf-8"))
        raise

    texto = data["candidates"][0]["content"]["parts"][0]["text"]

    # Por si el modelo añade ```json ... ``` a pesar de la instrucción
    texto_limpio = re.sub(r"^```json\s*|\s*```$", "", texto.strip())

    historia = json.loads(texto_limpio)

    with open("historia_generada.json", "w", encoding="utf-8") as f:
        json.dump(historia, f, ensure_ascii=False, indent=2)

    print(f"Historia generada: {historia['titulo']}")
    print(f"Fragmentos: {len(historia['fragmentos'])}")


if __name__ == "__main__":
    main()
