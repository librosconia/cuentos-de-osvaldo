"""
Lee historia_generada.json y genera un archivo de audio (voz de Osvaldo)
por cada fragmento, usando edge-tts (motor de voz de Microsoft Edge),
que es gratis, no necesita clave ni cuenta.

Guarda los audios en la carpeta audio/ como audio_001.mp3, audio_002.mp3, etc.
"""

import asyncio
import json
import os

import edge_tts

VOZ = "es-ES-AlvaroNeural"  # voz masculina en español de España


async def generar_audio(texto, ruta_salida):
    comunicador = edge_tts.Communicate(texto, voice=VOZ)
    await comunicador.save(ruta_salida)


async def main():
    with open("historia_generada.json", "r", encoding="utf-8") as f:
        historia = json.load(f)

    os.makedirs("audio", exist_ok=True)

    fallos = []
    for i, fragmento in enumerate(historia["fragmentos"], start=1):
        ruta = f"audio/audio_{i:03d}.mp3"
        print(f"Generando {ruta}...")
        try:
            await generar_audio(fragmento["texto"], ruta)
        except Exception as e:
            print(f"  SALTADO ({e})")
            fallos.append(ruta)

    total = len(historia["fragmentos"])
    print(f"Listo: {total - len(fallos)}/{total} audios generados en audio/")
    if fallos:
        print(f"Fallaron: {fallos}")


if __name__ == "__main__":
    asyncio.run(main())
