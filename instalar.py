"""Instala o Kit Dark Code no Claude Code deste computador.

  python instalar.py              instala para todas as pastas (em ~/.claude)
  python instalar.py --pasta X    instala só na pasta X (em X/.claude)
  python instalar.py --ver        só mostra o que seria feito, sem copiar nada

Só copia arquivos de texto (skills, agentes, modelos, prompts e scripts).
Não instala programas, não pede senha e não apaga nada: se uma skill ou um
agente com o mesmo nome já existir, a versão antiga é guardada com ".antigo".
"""
import argparse
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def copiar_pasta(origem, destino, ver):
    if destino.exists():
        antigo = destino.with_name(destino.name + ".antigo")
        if not ver:
            if antigo.exists():
                shutil.rmtree(antigo)
            destino.rename(antigo)
        print(f"  (já existia: guardei em {antigo.name})")
    if not ver:
        shutil.copytree(origem, destino)


def copiar_arquivo(origem, destino, ver):
    if destino.exists() and destino.read_bytes() != origem.read_bytes():
        antigo = destino.with_name(destino.name + ".antigo")
        if not ver:
            shutil.copy2(destino, antigo)
        print(f"  (já existia: guardei em {antigo.name})")
    if not ver:
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origem, destino)


def main():
    p = argparse.ArgumentParser(description="Instala o Kit Dark Code")
    p.add_argument("--pasta", help="instalar só nesta pasta (por exemplo, a pasta do canal)")
    p.add_argument("--ver", action="store_true", help="só mostrar, sem copiar")
    a = p.parse_args()
    base = (Path(a.pasta).expanduser().resolve() if a.pasta else Path.home()) / ".claude"
    if a.pasta and not Path(a.pasta).expanduser().is_dir():
        sys.exit(f"A pasta {a.pasta} não existe.")
    print(("Simulação: " if a.ver else "") + f"instalando o Kit Dark Code em {base}")

    skills = sorted(d for d in (AQUI / "skills").iterdir() if (d / "SKILL.md").exists())
    for d in skills:
        print(f"skill   /{d.name}")
        copiar_pasta(d, base / "skills" / d.name, a.ver)
    agentes = sorted((AQUI / "agentes").glob("*.md"))
    for f in agentes:
        print(f"agente  {f.stem}")
        copiar_arquivo(f, base / "agents" / f.name, a.ver)
    apoio = base / "dark-code"
    for nome in ("modelos", "prompts", "scripts"):
        for f in sorted((AQUI / nome).glob("*")):
            copiar_arquivo(f, apoio / nome / f.name, a.ver)
    for nome in ("MAPA.md", "VERSAO"):
        copiar_arquivo(AQUI / nome, apoio / nome, a.ver)
    print(f"apoio   modelos, prompts e scripts em {apoio}")
    print()
    print(f"Pronto: {len(skills)} skills e {len(agentes)} agentes" + (" (simulação, nada foi copiado)." if a.ver else " instalados."))
    if not a.ver:
        print("Abra uma sessão nova no Claude Code e digite / para ver as skills.")


if __name__ == "__main__":
    main()
