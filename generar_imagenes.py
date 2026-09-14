"""
Lee historia_generada.json (creado por generar_historia.py) y genera una imagen
por cada fragmento, usando el "prompt_imagen" de cada uno.

Usa la vía gratuita y anónima de Pollinations (image.pollinations.ai), sin
clave ni coste.

Para que Osvaldo se vea siempre parecido sin depender de un modelo de pago,
se usa siempre la MISMA descripción física exacta (fija en este script) más
una MISMA semilla (seed) fija para los fragmentos de tipo "narrador" — así
el resultado es mucho más consistente que si cada vez se describiera con
palabras distintas o con una semilla aleatoria.

Guarda las imágenes en la carpeta imagenes/ como imagen_001.png, imagen_002.png, etc.
"""

import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error

BASE_URL = "https://image.pollinations.ai/prompt/"
SEMILLA_OSVALDO = 87234  # semilla fija para que Osvaldo salga siempre parecido

DESCRIPCION_OSVALDO = (
    "Osvaldo, anciano contador de historias de terror. Pelo blanco despeinado, "
    "gorra marrón, ojos claros casi blancos, sonrisa torcida y siniestra, piel "
    "pálida y arrugada. Chaqueta marrón remendada, chaleco verde, camisa "
    "blanca, pañuelo beige al cuello, pantalón oscuro remendado, botas. "
    "Ilustración plana tipo cómic, líneas negras definidas, colores apagados "
    "(marrones, verdes, grises oscuros), sin sombreado realista, sin "
    "fotorrealismo."
)


def generar_imagen(prompt, ruta_salida, tipo, intentos=4):
    if tipo == "narrador":
        prompt_final = f"{DESCRIPCION_OSVALDO} {prompt}"
        semilla = SEMILLA_OSVALDO
    else:
        prompt_final = (
            "Ilustración plana tipo cómic, líneas negras definidas, colores "
            f"apagados, sin fotorrealismo. {prompt}"
        )
        semilla = None

    prompt_codificado = urllib.parse.quote(prompt_final)
    url = (
        f"{BASE_URL}{prompt_codificado}"
        "?width=1024&height=1024&nologo=true&model=flux&enhance=false"
    )
    if semilla is not None:
        url += f"&seed={semilla}"

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
            print(f"  intento {intento} fallido ({e.code}): {detalle[:300]}")
            time.sleep(18)
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
        time.sleep(16)  # límite de la vía gratuita: 1 imagen cada ~15s

    total = len(historia["fragmentos"])
    print(f"Listo: {total - len(fallos)}/{total} imágenes generadas en imagenes/")
    if fallos:
        print(f"Fallaron: {fallos}")


if __name__ == "__main__":
    main()
