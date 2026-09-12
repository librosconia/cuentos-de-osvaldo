"""
Lee historia_generada.json (creado por generar_historia.py) y genera una imagen
por cada fragmento, usando el "prompt_imagen" de cada uno.

Usa Pollinations.ai (https://pollinations.ai), que es gratis y no necesita clave.
Guarda las imágenes en la carpeta imagenes/ como imagen_001.png, imagen_002.png, etc.
"""

import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error

BASE_URL = "https://image.pollinations.ai/prompt/"


def generar_imagen(prompt, ruta_salida, intentos=3):
    prompt_codificado = urllib.parse.quote(prompt)
    url = (
        f"{BASE_URL}{prompt_codificado}"
        "?width=1024&height=1024&nologo=true&model=flux"
    )
    for intento in range(1, intentos + 1):
        try:
            urllib.request.urlretrieve(url, ruta_salida)
            return
        except urllib.error.HTTPError as e:
            print(f"  intento {intento} fallido ({e.code}), reintentando...")
            time.sleep(20)
    raise RuntimeError(f"No se pudo generar la imagen para: {ruta_salida}")


def main():
    with open("historia_generada.json", "r", encoding="utf-8") as f:
        historia = json.load(f)

    os.makedirs("imagenes", exist_ok=True)

    for i, fragmento in enumerate(historia["fragmentos"], start=1):
        ruta = f"imagenes/imagen_{i:03d}.png"
        print(f"Generando {ruta} ({fragmento['tipo']})...")
        generar_imagen(fragmento["prompt_imagen"], ruta)
        time.sleep(16)  # Pollinations limita a 1 petición cada 15 segundos

    print(f"Listo: {len(historia['fragmentos'])} imágenes generadas en imagenes/")


if __name__ == "__main__":
    main()
