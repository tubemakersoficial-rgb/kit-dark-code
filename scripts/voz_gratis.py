"""Narração com voz grátis (Edge-TTS). Roda no seu computador, sem conta e sem chave.

uso:
  python voz_gratis.py roteiro.txt audios/001-meu-video.mp3
  python voz_gratis.py roteiro.txt saida.mp3 --voz pt-BR-FranciscaNeural --velocidade -10%

instalar (uma vez):  pip install edge-tts
"""
import argparse
import asyncio
import sys
from pathlib import Path


async def gerar(texto, saida, voz, velocidade):
    import edge_tts
    await edge_tts.Communicate(texto, voz, rate=velocidade).save(str(saida))


def main():
    p = argparse.ArgumentParser(description="Narração grátis com Edge-TTS")
    p.add_argument("texto", help="arquivo .txt ou .md só com o texto narrado")
    p.add_argument("saida", help="arquivo .mp3 de saída")
    p.add_argument("--voz", default="pt-BR-AntonioNeural", help="pt-BR-AntonioNeural (masculina) ou pt-BR-FranciscaNeural (feminina)")
    p.add_argument("--velocidade", default="+0%", help="exemplos: -10%% (mais calma), +10%% (mais rápida)")
    a = p.parse_args()
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        sys.exit("Falta o edge-tts. Instale com:  pip install edge-tts")
    texto = Path(a.texto).read_text(encoding="utf-8").strip()
    if not texto:
        sys.exit("O arquivo de texto está vazio.")
    saida = Path(a.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(gerar(texto, saida, a.voz, a.velocidade))
    print(f"Áudio salvo em {saida} ({len(texto.split())} palavras, voz {a.voz})")


if __name__ == "__main__":
    main()
