"""Música de fundo e sons de ambiente por baixo da narração, no volume certo.

Como usar (na pasta do canal):
  python trilha.py conferir audios/trilha/
      mostra cada arquivo: de onde veio (pelo nome), duração e volume
  python trilha.py mixar --voz audios/001-abertura.mp3 --musica audios/trilha/youtube-musica.mp3 \\
         --ambiente audios/trilha/youtube-fogo.mp3 audios/trilha/youtube-vento.mp3 \\
         --saida audios/001-abertura-com-trilha.mp3
      mistura tudo e mostra a tabela de volumes

Como a mistura funciona:
  - O volume de cada camada é medido (em LUFS) e ajustado em relação à voz: a música fica
    --musica-db abaixo da voz (padrão 18) e cada ambiente --ambiente-db abaixo (padrão 26).
  - Quando a voz fala, a música abaixa sozinha uns 7 dB (ducking) e volta nas pausas.
  - A música entra devagar, a voz começa depois de --antes segundos e tudo some devagar
    --depois segundos após a voz acabar.
  - Sons curtos são repetidos com uma emenda suave (crossfade), sem estalo.
  - O volume final fica em --lufs (padrão -14, comum no YouTube; história para dormir pode usar -16).
  - A narração original não é alterada.

O nome do arquivo diz de onde ele veio: youtube-, freesound-cc0-, freesound-by-, pixabay-,
flowmusic-pago-. Arquivo sem esse começo aparece como "origem desconhecida".

Precisa de: Python, numpy e FFmpeg (aula 0.7). O numpy já vem com o Whisper (aula 0.8).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TAXA = 48000
EXTENSOES = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".opus"}
ORIGENS = [
    ("youtube-", "Biblioteca de áudio do YouTube", "Sem Content ID. Se a faixa for Creative Commons, copie o crédito no ícone de licença da Biblioteca."),
    ("freesound-cc0-", "Freesound, licença zero (cc0)", "Pode usar sem crédito."),
    ("freesound-by-nc-", "Freesound, atribuição NÃO comercial", "NÃO use em canal monetizado."),
    ("freesound-by-", "Freesound, atribuição (by)", "Precisa de crédito na descrição: nome do autor e link do som."),
    ("freesound-", "Freesound, licença não informada no nome", "Confira a licença na página do som antes de usar."),
    ("pixabay-", "Pixabay", "Sem crédito obrigatório. Baixe também o certificado de licença, para o caso de reivindicação."),
    ("flowmusic-pago-", "Flow Music, plano pago", "O Google lista uso comercial nos planos pagos."),
    ("flowmusic-", "Flow Music, plano não informado", "No plano grátis o Google não lista uso comercial. Confirme o plano."),
]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def exigir_ffmpeg():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        sys.exit("Falta o FFmpeg. A aula 0.7 instala com um prompt.")


def origem(arq):
    nome = Path(arq).name.lower()
    for prefixo, fonte, aviso in ORIGENS:
        if nome.startswith(prefixo):
            return fonte, aviso
    return "origem desconhecida", "Não use até saber de onde veio e qual é a licença. Renomeie com o site no começo."


def duracao(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        sys.exit(f"Não consegui ler o arquivo {arq}. Ele é mesmo um áudio?")


def lufs(arq):
    """Volume médio (LUFS integrado) e pico verdadeiro (dBTP)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(arq), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)
    if not m:
        sys.exit(f"Não consegui medir o volume de {arq}.")
    d = json.loads(m.group(0))
    i, tp = float(d["input_i"]), float(d["input_tp"])
    return (None if i < -70 else i), tp


def ler(arq):
    import numpy as np
    bruto = subprocess.run(["ffmpeg", "-v", "error", "-i", str(arq), "-f", "f32le", "-ac", "2", "-ar", str(TAXA), "-"],
                           capture_output=True, check=True).stdout
    return np.frombuffer(bruto, dtype=np.float32).reshape(-1, 2).copy()


def gravar_wav(dados, arq):
    import numpy as np
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(TAXA), "-i", "-", "-c:a", "pcm_f32le", str(arq)],
                   input=np.ascontiguousarray(dados, dtype=np.float32).tobytes(), check=True)


def repetir(dados, segundos, emenda=1.0):
    """Repete o som até a duração pedida, com crossfade de potência constante em cada emenda."""
    import numpy as np
    alvo = int(segundos * TAXA)
    if len(dados) >= alvo:
        return dados[:alvo]
    f = min(int(emenda * TAXA), len(dados) // 3)
    if f < 64:
        return np.tile(dados, (alvo // max(len(dados), 1) + 1, 1))[:alvo]
    t = np.linspace(0, np.pi / 2, f, dtype=np.float32)[:, None]
    sai, entra = np.cos(t), np.sin(t)
    saida = dados.copy()
    while len(saida) < alvo:
        saida = np.concatenate([saida[:-f], saida[-f:] * sai + dados[:f] * entra, dados[f:]])
    return saida[:alvo]


def cmd_conferir(a):
    exigir_ffmpeg()
    pasta = Path(a.pasta)
    arqs = sorted(p for p in pasta.iterdir() if p.suffix.lower() in EXTENSOES) if pasta.is_dir() else []
    if not arqs:
        sys.exit(f"Nenhum áudio em {pasta}.")
    problemas = 0
    print(f"{'arquivo':<34} {'duração':>8} {'volume':>10}  origem")
    for p in arqs:
        i, tp = lufs(p)
        fonte, aviso = origem(p)
        vol = f"{i:.1f} LUFS" if i is not None else "silêncio"
        print(f"{p.name:<34} {duracao(p):7.1f}s {vol:>10}  {fonte}")
        print(f"{'':<34} {'':>8} {'':>10}  -> {aviso}")
        if fonte == "origem desconhecida" or "NÃO" in aviso:
            problemas += 1
    print()
    print("Tudo com origem conhecida." if not problemas else f"{problemas} arquivo(s) precisam de atenção antes de entrar no vídeo.")


def cmd_mixar(a):
    exigir_ffmpeg()
    import numpy as np
    voz_arq = Path(a.voz)
    camadas = ([("música", Path(a.musica), -a.musica_db)] if a.musica else []) + [("ambiente", Path(p), -a.ambiente_db) for p in a.ambiente or []]
    for _, p, _ in camadas + [("voz", voz_arq, 0)]:
        if not p.exists():
            sys.exit(f"Não achei {p}.")
    for nome, p, _ in camadas:
        fonte, aviso = origem(p)
        if fonte == "origem desconhecida" or "NÃO" in aviso:
            if not a.mesmo_assim:
                sys.exit(f"{p.name}: {fonte}. {aviso} (Se a pessoa confirmou a origem, renomeie o arquivo ou use --mesmo-assim.)")
    if not camadas:
        sys.exit("Passe pelo menos --musica ou --ambiente.")

    voz_i, _ = lufs(voz_arq)
    if voz_i is None:
        sys.exit("A narração está em silêncio.")
    voz_dur = duracao(voz_arq)
    total = a.antes + voz_dur + a.depois

    tmp = Path(tempfile.mkdtemp(prefix="trilha-"))
    try:
        entradas, filtros, tabela = [], [], []
        # voz: entra depois de --antes segundos; é dividida em duas (uma vai para a mistura, a outra comanda o ducking)
        entradas += ["-i", str(voz_arq)]
        ms = int(a.antes * 1000)
        filtros.append(f"[0:a]aresample={TAXA},aformat=channel_layouts=stereo,adelay={ms}|{ms},apad,atrim=0:{total:.3f},asplit=2[voz][sc0]")
        # o ducking é comandado por uma cópia da voz levada a -16 LUFS, para abaixar igual com qualquer narração
        filtros.append(f"[sc0]volume={-16 - voz_i:.2f}dB[sc]")
        tabela.append(("voz", voz_arq.name, voz_i, 0.0, voz_i))
        rotulos = ["[voz]"]
        for n, (nome, p, rel) in enumerate(camadas, 1):
            i, _ = lufs(p)
            if i is None:
                sys.exit(f"{p.name} está em silêncio.")
            ganho = (voz_i + rel) - i
            dados = repetir(ler(p), total, a.emenda)
            wav = tmp / f"camada{n}.wav"
            gravar_wav(dados * np.float32(10 ** (ganho / 20)), wav)
            entradas += ["-i", str(wav)]
            fade_fim = max(total - a.fade_saida, 0)
            cadeia = f"[{n}:a]afade=t=in:st=0:d={a.fade_entrada},afade=t=out:st={fade_fim:.3f}:d={a.fade_saida}"
            if nome == "música" and not a.sem_ducking:
                cadeia += f"[m{n}];[m{n}][sc]sidechaincompress=threshold=0.06:ratio=3:attack=30:release=600:makeup=1[c{n}]"
            else:
                cadeia += f"[c{n}]"
            filtros.append(cadeia)
            rotulos.append(f"[c{n}]")
            tabela.append((nome, p.name, i, ganho, voz_i + rel))
        if a.sem_ducking or not a.musica:
            filtros[0] = filtros[0].replace(",asplit=2[voz][sc0]", "[voz]")
            filtros.pop(1)  # sem ducking, a cópia da voz que comandava a música não é usada
        filtros.append(f"{''.join(rotulos)}amix=inputs={len(rotulos)}:normalize=0:duration=first,"
                       f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11,aresample={TAXA}[saida]")
        saida = Path(a.saida)
        saida.parent.mkdir(parents=True, exist_ok=True)
        if saida.resolve() == voz_arq.resolve():
            sys.exit("A saída não pode ser o arquivo da narração: a narração original fica guardada.")
        comando = ["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtros), "-map", "[saida]", "-t", f"{total:.3f}"]
        comando += ["-c:a", "libmp3lame", "-b:a", "192k"] if saida.suffix.lower() == ".mp3" else []
        r = subprocess.run(comando + [str(saida)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            sys.exit(f"O FFmpeg falhou: {r.stderr.strip()[:500]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    final_i, final_tp = lufs(saida)
    print(f"Pronto: {saida}  ({total:.1f}s: {a.antes:g}s antes da voz, {voz_dur:.1f}s de voz, {a.depois:g}s depois)\n")
    print(f"| Camada | Arquivo | Volume original | Ajuste | Volume na mistura (antes do ajuste final) |")
    print(f"|---|---|---|---|---|")
    for nome, arq, i, g, alvo in tabela:
        print(f"| {nome} | {arq} | {i:.1f} LUFS | {g:+.1f} dB | {alvo:.1f} LUFS ({alvo - voz_i:+.0f} em relação à voz) |")
    partes = []
    if a.musica:
        partes.append(f"Música {a.musica_db:g} dB abaixo da voz" + (", sem ducking" if a.sem_ducking else ", e uns 7 dB mais baixa enquanto a voz fala"))
    if a.ambiente:
        partes.append(f"Ambiente {a.ambiente_db:g} dB abaixo da voz")
    print("\n" + ". ".join(partes) + ".")
    print(f"Volume final: {final_i:.1f} LUFS (alvo {a.lufs:g}), pico {final_tp:.1f} dBTP.")


def main():
    ap = argparse.ArgumentParser(description="Música e ambiente por baixo da narração",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("conferir", help="mostra origem, duração e volume de cada arquivo")
    c.add_argument("pasta")
    m = sub.add_parser("mixar", help="mistura voz, música e ambiente")
    m.add_argument("--voz", required=True)
    m.add_argument("--musica")
    m.add_argument("--ambiente", nargs="+")
    m.add_argument("--saida", required=True)
    m.add_argument("--musica-db", type=float, default=18, help="quantos dB a música fica abaixo da voz (padrão 18)")
    m.add_argument("--ambiente-db", type=float, default=26, help="quantos dB cada ambiente fica abaixo da voz (padrão 26)")
    m.add_argument("--lufs", type=float, default=-14, help="volume final (padrão -14)")
    m.add_argument("--antes", type=float, default=2.0, help="segundos de trilha antes da voz")
    m.add_argument("--depois", type=float, default=3.0, help="segundos de trilha depois da voz")
    m.add_argument("--fade-entrada", type=float, default=2.5)
    m.add_argument("--fade-saida", type=float, default=3.0)
    m.add_argument("--emenda", type=float, default=1.0, help="segundos de crossfade ao repetir um som curto")
    m.add_argument("--sem-ducking", action="store_true")
    m.add_argument("--mesmo-assim", action="store_true", help="aceita arquivo de origem desconhecida (só se a pessoa confirmou)")
    a = ap.parse_args()
    {"conferir": cmd_conferir, "mixar": cmd_mixar}[a.cmd](a)


if __name__ == "__main__":
    main()
