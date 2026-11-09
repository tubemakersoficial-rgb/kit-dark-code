"""
Tira o fundo de uma imagem com o rembg e tampa os buracos que ficam dentro da figura.

Como usar (na pasta do canal):
    python ferramentas/recortar.py imagens/001-o-farol-abandonado.png

Isso cria imagens/001-o-farol-abandonado-sem-fundo.png ao lado da original.
Pode passar várias imagens de uma vez:
    python ferramentas/recortar.py imagens/cena1.png imagens/cena2.png

Por que tampar buracos: o rembg às vezes confunde partes escuras DENTRO da figura
(olhos, boca, sombras) com o fundo e deixa essas partes transparentes. Aqui, qualquer
área transparente cercada pela figura por todos os lados volta a ficar visível.

Se a figura tiver um vão de verdade no meio (uma janela, uma rosquinha, um arco),
use --sem-tampar no final para manter esse vão transparente:
    python ferramentas/recortar.py imagens/porta.png --sem-tampar
"""
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image
from rembg import new_session, remove
from scipy.ndimage import binary_fill_holes

MODELO = "bria-rmbg"


def tampar_buracos(recorte):
    alfa = np.array(recorte.getchannel("A"))
    figura = alfa > 127
    buracos = binary_fill_holes(figura) & ~figura
    alfa[buracos] = 255
    recorte.putalpha(Image.fromarray(alfa))
    return int(buracos.sum())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tampar = "--sem-tampar" not in sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    sessao = new_session(MODELO)
    for nome in args:
        entrada = Path(nome)
        saida = entrada.with_name(f"{entrada.stem}-sem-fundo.png")
        inicio = time.time()

        imagem = Image.open(entrada).convert("RGB")
        recorte = remove(imagem, session=sessao).convert("RGBA")
        tampados = tampar_buracos(recorte) if tampar else 0
        recorte.save(saida)

        aviso = f", {tampados} pixels de buraco tampados" if tampados else ""
        print(f"{saida}  ({time.time() - inicio:.1f}s{aviso})")


if __name__ == "__main__":
    main()
