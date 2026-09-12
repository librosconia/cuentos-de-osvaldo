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
TOKEN = os.environ.get("POLLINATIONS_TOKEN", "")
IMAGEN_REFERENCIA_OSVALDO = (
    "https://raw.githubusercontent.com/librosconia/cuentos-de-osvaldo/main/osvaldo_referencia.png"
)


def generar_imagen(prompt, ruta_salida, tipo, intentos=3):
    prompt_codificado = urllib.parse.quote(prompt)
    if tipo == "narrador":
        # Kontext genera a partir de la imagen de referencia, para que Osvaldo
        # se vea siempre igual en lugar de que la IA se lo invente cada vez.
        imagen_ref_codificada = urllib.parse.quote(IMAGEN_REFERENCIA_OSVALDO, safe="")
        url = (
            f"{BASE_URL}{prompt_codificado}"
            f"?width=1024&height=1024&nologo=true&model=kontext"
            f"&image={imagen_ref_codificada}&enhance=false"
        )
    else:
        url = (
            f"{BASE_URL}{prompt_codificado}"
            "?width=1024&height=1024&nologo=true&model=flux&enhance=false"
        )
    if TOKEN:
        url += f"&token={TOKEN}"
    for intento in range(1, intentos + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0 Safari/537.36"
                    )
                },
            )
            with urllib.request.urlopen(req) as resp, open(ruta_salida, "wb") as f:
                f.write(resp.read())
            return
        except urllib.error.HTTPError as e:
            detalle = e.read().decode("utf-8", errors="replace")
            print(f"  intento {intento} fallido ({e.code}): {detalle[:500]}")
            time.sleep(20)


def main():
    with open("historia_generada.json", "r", encoding="utf-8") as f:
        historia = json.load(f)

    os.makedirs("imagenes", exist_ok=True)

    for i, fragmento in enumerate(historia["fragmentos"], start=1):
        ruta = f"imagenes/imagen_{i:03d}.png"
        print(f"Generando {ruta} ({fragmento['tipo']})...")
        generar_imagen(fragmento["prompt_imagen"], ruta, fragmento["tipo"])
        time.sleep(16)  # Pollinations limita a 1 petición cada 15 segundos

    print(f"Listo: {len(historia['fragmentos'])} imágenes generadas en imagenes/")


if __name__ == "__main__":
    main()
