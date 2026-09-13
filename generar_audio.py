"""
Lee historia_generada.json y genera un archivo de audio (voz de Osvaldo)
por cada fragmento, usando la voz "onyx" de Pollinations (gen.pollinations.ai).

Necesita la variable de entorno POLLINATIONS_TOKEN.
Guarda los audios en la carpeta audio/ como audio_001.mp3, audio_002.mp3, etc.
"""

import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error

BASE_URL = "https://gen.pollinations.ai/audio/"
TOKEN = os.environ.get("POLLINATIONS_TOKEN", "")
VOZ = "onyx"

if not TOKEN:
    raise SystemExit("Falta la variable de entorno POLLINATIONS_TOKEN")


def generar_audio(texto, ruta_salida, intentos=3):
    texto_codificado = urllib.parse.quote(texto)
    url = f"{BASE_URL}{texto_codificado}?voice={VOZ}"
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
            print(f"  intento {intento} fallido ({e.code}): {detalle[:300]}")
            time.sleep(15)
    raise RuntimeError(f"No se pudo generar el audio para: {ruta_salida}")


def main():
    with open("historia_generada.json", "r", encoding="utf-8") as f:
        historia = json.load(f)

    os.makedirs("audio", exist_ok=True)

    fallos = []
    for i, fragmento in enumerate(historia["fragmentos"], start=1):
        ruta = f"audio/audio_{i:03d}.mp3"
        print(f"Generando {ruta}...")
        try:
            generar_audio(fragmento["texto"], ruta)
        except RuntimeError as e:
            print(f"  SALTADO: {e}")
            fallos.append(ruta)
        time.sleep(3)

    total = len(historia["fragmentos"])
    print(f"Listo: {total - len(fallos)}/{total} audios generados en audio/")
    if fallos:
        print(f"Fallaron: {fallos}")


if __name__ == "__main__":
    main()
