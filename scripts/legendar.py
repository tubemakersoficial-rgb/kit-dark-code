"""
Transcreve uma narração com o Whisper e gera a legenda .srt ao lado do áudio.

Como usar (na pasta do canal):
    python ferramentas/legendar.py audios/001-o-farol-abandonado.mp3

Isso cria audios/001-o-farol-abandonado.srt e mostra o texto transcrito.
Para outro idioma, acrescente o código no final, por exemplo:  en
"""
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

MODELO = "mobiuslabsgmbh/faster-whisper-large-v3-turbo"


def tempo_srt(segundos):
    ms = int(round(segundos * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def ler_audio(caminho):
    # O ffmpeg lê o áudio (o leitor embutido do faster-whisper falha com a versão do PyAV instalada).
    bruto = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(caminho), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(bruto, dtype=np.float32)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    audio = Path(sys.argv[1])
    idioma = sys.argv[2] if len(sys.argv) > 2 else "pt"
    srt = audio.with_suffix(".srt")

    inicio = time.time()
    modelo = WhisperModel(MODELO, device="cpu", compute_type="int8")
    segmentos, info = modelo.transcribe(ler_audio(audio), language=idioma, vad_filter=True)
    segmentos = list(segmentos)

    with open(srt, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segmentos, 1):
            f.write(f"{i}\n{tempo_srt(seg.start)} --> {tempo_srt(seg.end)}\n{seg.text.strip()}\n\n")

    print("TEXTO:")
    print(" ".join(seg.text.strip() for seg in segmentos))
    print(f"\nLegenda salva em {srt}")
    print(f"{len(segmentos)} legendas, {info.duration:.1f}s de áudio, {time.time() - inicio:.1f}s para transcrever")


if __name__ == "__main__":
    main()
