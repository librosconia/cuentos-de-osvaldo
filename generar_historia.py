"""
Lee historia_generada.json (creado por generar_historia.py) y genera una imagen
por cada fragmento, usando el "prompt_imagen" de cada uno.

Usa la puerta de enlace gen.pollinations.ai, autenticada con la clave gratuita
de Pollinations (variable de entorno POLLINATIONS_TOKEN).

Los fragmentos de tipo "narrador" usan el modelo Kontext junto con la imagen
de referencia de Osvaldo, para que su cara se mantenga siempre igual.
Los fragmentos de tipo "escena" usan el modelo Flux normal (solo texto).

Guarda las imágenes en la carpeta imagenes/ como imagen_001.png, imagen_002.png, etc.
"""

import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error

BASE_URL = "https://gen.pollinations.ai/image/"
TOKEN = os.environ.get("POLLINATIONS_TOKEN", "")
IMAGEN_REFERENCIA_OSVALDO = (
    "https://raw.githubusercontent.com/librosconia/cuentos-de-osvaldo/main/osvaldo_referencia.png"
)

if not TOKEN:
    raise SystemExit("Falta la variable de entorno POLLINATIONS_TOKEN")


def generar_imagen(prompt, ruta_salida, tipo, intentos=3):
    prompt_codificado = urllib.parse.quote(prompt)
    if tipo == "narrador":
        imagen_ref_codificada = urllib.parse.quote(IMAGEN_REFERENCIA_OSVALDO, safe="")
        url = (
            f"{BASE_URL}{prompt_codificado}"
            f"?model=kontext&image={imagen_ref_codificada}&width=1024&height=1024"
        )
    else:
        url = f"{BASE_URL}{prompt_codificado}?model=flux&width=1024&height=1024"

    for intento in range(1, intentos + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bearer {TOKEN}",
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0 Safari/537.36"
                    ),
                },
            )
            with urllib.request.urlopen(req) as resp, open(ruta_salida, "wb") as f:
                f.write(resp.read())
            return
        except urllib.error.HTTPError as e:
            detalle = e.read().decode("utf-8", errors="replace")
            print(f"  intento {intento} fallido ({e.code}): {detalle[:500]}")
            time.sleep(15)
    raise RuntimeError(f"No se pudo generar la imagen para: {ruta_salida}")


def main():
    with open("historia_generada.json", "r", encoding="utf-8") as f:
        historia = json.load(f)

    os.makedirs("imagenes", exist_ok=True)

    fallos = []
    for i, fragmento in enumerate(historia["fragmentos"], start=1):
        ruta = f"imagenes/imagen_{i:03d}.png"
        print(f"Generando {ruta} ({fragmento['tipo']})...")
        try:
            generar_imagen(fragmento["prompt_imagen"], ruta, fragmento["tipo"])
        except RuntimeError as e:
            print(f"  SALTADA: {e}")
            fallos.append(ruta)
        time.sleep(3)

    total = len(historia["fragmentos"])
    print(f"Listo: {total - len(fallos)}/{total} imágenes generadas en imagenes/")
    if fallos:
        print(f"Fallaron: {fallos}")


if __name__ == "__main__":
    main()
