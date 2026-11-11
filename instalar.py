"""Instala o Kit Dark Code no Claude Code deste computador.

  python instalar.py              instala para todas as pastas (em ~/.claude)
  python instalar.py --pasta X    instala só na pasta X (em X/.claude)
  python instalar.py --ver        só mostra o que seria feito, sem copiar nada

Só copia arquivos de texto (skills, agentes, modelos, prompts e scripts).
Não instala programas, não pede senha e não apaga nada: se uma skill ou um
agente com o mesmo nome já existir, a versão antiga é guardada em
.claude/dark-code/versoes-antigas.
"""
import argparse
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent


GUARDA = None  # pasta onde ficam as versões antigas (fora de skills/ e agents/, para não aparecerem em dobro)


def iguais(a, b):
    if a.is_file():
        return b.is_file() and a.read_bytes() == b.read_bytes()
    fa = sorted(p.relative_to(a) for p in a.rglob("*") if p.is_file())
    fb = sorted(p.relative_to(b) for p in b.rglob("*") if p.is_file())
    return fa == fb and all((a / f).read_bytes() == (b / f).read_bytes() for f in fa)


def guardar(destino, ver):
    alvo = GUARDA / destino.parent.name / destino.name
    print(f"  (já existia uma versão diferente: guardei em {alvo})")
    if not ver:
        if alvo.exists():
            shutil.rmtree(alvo) if alvo.is_dir() else alvo.unlink()
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(destino), str(alvo))


def copiar_pasta(origem, destino, ver):
    if destino.exists():
        if iguais(origem, destino):
            return
        guardar(destino, ver)
    if not ver:
        shutil.copytree(origem, destino)


def copiar_arquivo(origem, destino, ver):
    if destino.exists():
        if iguais(origem, destino):
            return
        guardar(destino, ver)
    if not ver:
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origem, destino)


def main():
    p = argparse.ArgumentParser(description="Instala o Kit Dark Code")
    p.add_argument("--pasta", help="instalar só nesta pasta (por exemplo, a pasta do canal)")
    p.add_argument("--ver", action="store_true", help="só mostrar, sem copiar")
    a = p.parse_args()
    global GUARDA
    base = (Path(a.pasta).expanduser().resolve() if a.pasta else Path.home()) / ".claude"
    GUARDA = base / "dark-code" / "versoes-antigas"
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
