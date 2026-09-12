"""
Lee historia_generada.json (creado por generar_historia.py) y genera una imagen
por cada fragmento, usando el "prompt_imagen" de cada uno.

Necesita la variable de entorno GEMINI_API_KEY.
Guarda las imágenes en la carpeta imagenes/ como imagen_001.png, imagen_002.png, etc.
"""

import os
import json
import base64
import urllib.request
import urllib.error

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit("Falta la variable de entorno GEMINI_API_KEY")

MODEL = "gemini-2.5-flash-image-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"


def generar_imagen(prompt, ruta_salida):
    body = {"contents": [{"parts": [{"text": prompt}]}]}
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
        print(f"ERROR generando '{ruta_salida}':")
        print(e.read().decode("utf-8"))
        raise

    partes = data["candidates"][0]["content"]["parts"]
    imagen_b64 = next(p["inlineData"]["data"] for p in partes if "inlineData" in p)

    with open(ruta_salida, "wb") as f:
        f.write(base64.b64decode(imagen_b64))


def main():
    with open("historia_generada.json", "r", encoding="utf-8") as f:
        historia = json.load(f)

    os.makedirs("imagenes", exist_ok=True)

    for i, fragmento in enumerate(historia["fragmentos"], start=1):
        ruta = f"imagenes/imagen_{i:03d}.png"
        print(f"Generando {ruta} ({fragmento['tipo']})...")
        generar_imagen(fragmento["prompt_imagen"], ruta)

    print(f"Listo: {len(historia['fragmentos'])} imágenes generadas en imagenes/")


if __name__ == "__main__":
    main()
