"""
Junta las imágenes (imagenes/) y los audios (audio/) en un único vídeo final,
donde cada imagen se muestra exactamente lo que dura su audio correspondiente.

Necesita ffmpeg y ffprobe instalados (ya vienen en los runners de GitHub Actions).
Guarda el resultado en video_final.mp4
"""

import json
import os
import subprocess


def duracion_audio(ruta):
    resultado = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            ruta,
        ],
        capture_output=True, text=True, check=True,
    )
    return float(resultado.stdout.strip())


def crear_clip(imagen, audio, duracion, salida):
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-loop", "1", "-i", imagen,
            "-i", audio,
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", str(duracion),
            "-vf", "scale=1024:1024",
            salida,
        ],
        check=True, capture_output=True, text=True,
    )


def main():
    with open("historia_generada.json", "r", encoding="utf-8") as f:
        historia = json.load(f)

    total = len(historia["fragmentos"])
    os.makedirs("clips", exist_ok=True)

    lista_clips = []
    for i in range(1, total + 1):
        imagen = f"imagenes/imagen_{i:03d}.png"
        audio = f"audio/audio_{i:03d}.mp3"
        if not (os.path.exists(imagen) and os.path.exists(audio)):
            print(f"Fragmento {i}: falta imagen o audio, se salta.")
            continue

        duracion = duracion_audio(audio)
        clip = f"clips/clip_{i:03d}.mp4"
        print(f"Creando {clip} ({duracion:.1f}s)...")
        crear_clip(imagen, audio, duracion, clip)
        lista_clips.append(clip)

    if not lista_clips:
        raise SystemExit("No hay clips para montar el vídeo, revisa imágenes y audio.")

    with open("lista_clips.txt", "w", encoding="utf-8") as f:
        for clip in lista_clips:
            f.write(f"file '{clip}'\n")

    print("Uniendo todos los clips en el vídeo final...")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", "lista_clips.txt",
            "-c", "copy",
            "video_final.mp4",
        ],
        check=True, capture_output=True, text=True,
    )
    print(f"Listo: video_final.mp4 con {len(lista_clips)}/{total} fragmentos.")


if __name__ == "__main__":
    main()
