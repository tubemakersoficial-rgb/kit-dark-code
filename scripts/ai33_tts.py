"""Narração com voz de IA pelo ai33.pro (vozes do ElevenLabs e de outras plataformas).

A chave NUNCA aparece na tela nem na conversa. O script lê a chave sozinho, nesta ordem:
  1. variável de ambiente AI33_API_KEY
  2. arquivo ai33_key.txt na sua pasta de usuário (só a chave, numa linha)

Como usar (na pasta do canal):
  python ai33_tts.py chave
      confere se a chave existe e funciona, e mostra os créditos
  python ai33_tts.py vozes --busca portuguese --genero male
      lista vozes com o link da prévia de cada uma (não gasta créditos)
  python ai33_tts.py roteiro roteiros/001-meu-video.md --ver
      mostra o que vai ser narrado, em quantos trechos, e quanto vai custar (não gasta créditos)
  python ai33_tts.py roteiro roteiros/001-meu-video.md --voz elevenlabs_XXXX --so-abertura
      narra só a abertura, para ouvir antes de gastar com o resto
  python ai33_tts.py roteiro roteiros/001-meu-video.md --voz elevenlabs_XXXX --pode-gastar
      narra o roteiro inteiro e junta tudo em audios/001-meu-video.mp3
  python ai33_tts.py conferir roteiros/001-meu-video.md
      confere cada trecho com o Whisper e diz quais refazer
  python ai33_tts.py roteiro roteiros/001-meu-video.md --voz elevenlabs_XXXX --refazer 7 12
      gera de novo só os trechos 7 e 12 e junta outra vez
  python ai33_tts.py falar --voz elevenlabs_XXXX --texto "Boa noite." --saida audios/teste.mp3

Como o roteiro é lido:
  - Num .md, a narração começa no título que tem a palavra ABERTURA e para no título
    "Mapa de retenção", "Fatos", "Fontes", "Referências" ou "Notas".
  - Títulos (#), linhas de imagem (🎞), citações (>), tabelas (|) e listas (-) não são narrados.
  - [pausa] vira um silêncio (1,5 s); [pausa longa ...] vira um silêncio maior (12 s);
    [pausa 3s] vira 3 segundos. Outras marcações entre colchetes são ignoradas.
  - Num .txt, tudo é narrado, e as marcações [pausa] valem do mesmo jeito.

Cada trecho fica guardado em audios/.partes-NOME/. Se você mudar uma frase do roteiro e rodar de novo,
só o trecho que mudou é gerado outra vez; o resto é reaproveitado sem gastar créditos.

Precisa de: Python e FFmpeg (aula 0.7). Para conferir: faster-whisper (aula 0.8).
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

BASE = "https://api.ai33.pro"
AGENTE = "dark-code-kit/0.2"
MODELO_WHISPER = "mobiuslabsgmbh/faster-whisper-large-v3-turbo"
LIMITE_SEM_APROVACAO = 3000      # créditos estimados; acima disso precisa de --pode-gastar
CREDITOS_POR_CARACTERE = 1.15    # medido em 12/11/2026: cerca de 1,12 (476 créditos para 426 caracteres), com folga
TAMANHO_MAX_TRECHO = 2500        # caracteres por pedido; trechos maiores são divididos nos parágrafos
AO_MESMO_TEMPO = 4               # pedidos simultâneos ao ai33

INICIO = re.compile(r"abertura", re.I)
FIM = re.compile(r"mapa de reten|fatos|fontes|refer[eê]ncias|notas", re.I)
MARCA = re.compile(r"\[([^\]]*)\]")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# ------------------------------------------------------------------ chave e API
def chave():
    k = os.environ.get("AI33_API_KEY", "").strip()
    origem = "variável AI33_API_KEY"
    if not k:
        arq = Path.home() / "ai33_key.txt"
        origem = str(arq)
        if arq.exists():
            k = arq.read_text(encoding="utf-8-sig").strip()
    if not k:
        sys.exit("Não achei a chave do ai33. Copie a chave na página API Document do ai33 e salve "
                 f"num arquivo chamado ai33_key.txt na sua pasta de usuário ({Path.home()}), só a chave, numa linha. "
                 "Não cole a chave na conversa.")
    if " " in k or "\n" in k:
        sys.exit(f"O arquivo da chave ({origem}) tem espaços ou mais de uma linha. Deixe só a chave, numa linha.")
    return k, origem


def pedir(metodo, caminho, campos=None, query=None, tentativas=3):
    url = BASE + caminho
    if query:
        url += "?" + urllib.parse.urlencode({k: v for k, v in query.items() if v not in (None, "")})
    k, _ = chave()
    cab = {"xi-api-key": k, "User-Agent": AGENTE}
    corpo = None
    if campos is not None:
        limite = "----darkcode" + uuid.uuid4().hex
        partes = [f"--{limite}\r\nContent-Disposition: form-data; name=\"{n}\"\r\n\r\n{v}\r\n"
                  for n, v in campos.items() if v is not None]
        partes.append(f"--{limite}--\r\n")
        corpo = "".join(partes).encode("utf-8")
        cab["Content-Type"] = f"multipart/form-data; boundary={limite}"
    for n in range(tentativas):
        req = urllib.request.Request(url, data=corpo, headers=cab, method=metodo)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            texto = e.read().decode("utf-8", "replace")[:300].replace(k, "***")
            if e.code in (401, 403):
                sys.exit("O ai33 recusou a chave. Copie a chave de novo na página API Document e salve no arquivo ai33_key.txt.")
            if e.code == 402 or "credit" in texto.lower() and e.code < 500:
                sys.exit(f"O ai33 disse que faltam créditos ({e.code}). Compre créditos no site e rode de novo: o que já foi gerado fica guardado.")
            if e.code >= 500 and n < tentativas - 1:
                time.sleep(5 * (n + 1)); continue
            sys.exit(f"Erro {e.code} do ai33 em {caminho}: {texto}")
        except (urllib.error.URLError, TimeoutError) as e:
            if n < tentativas - 1:
                time.sleep(5 * (n + 1)); continue
            sys.exit(f"Sem conexão com o ai33 ({e}). Confira a internet e rode de novo: o que já foi gerado fica guardado.")


def baixar(url, destino):
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".baixando")
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f)
    tmp.replace(destino)
    return destino


def saldo():
    """Devolve (número ou None, resposta). O formato da resposta pode mudar, então procura o campo."""
    r = pedir("GET", "/v1/credits")
    def achar(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if any(p in k.lower() for p in ("credit", "balance", "saldo")) and isinstance(v, (int, float)) and not isinstance(v, bool):
                    return v
            for v in x.values():
                a = achar(v)
                if a is not None:
                    return a
        return None
    return achar(r), r


def pedir_voz(texto, voz, velocidade, nome):
    r = pedir("POST", "/v3/text-to-speech", campos={
        "text": texto, "voice_id": voz, "speed": str(velocidade),
        "with_transcript": "false", "file_name": nome})
    if not r.get("success") or not r.get("task_id"):
        sys.exit(f"O ai33 não aceitou o pedido: {r}")
    return r["task_id"]


def ver_tarefa(task_id):
    return pedir("GET", f"/v1/task/{task_id}")


# ------------------------------------------------------------------ leitura do roteiro
def limpar(linha):
    s = re.sub(r"(\*\*|__|\*|_|`)", "", linha)
    return re.sub(r"\s+", " ", s).strip()


def segundos_da_pausa(marca, curta, longa):
    m = marca.lower()
    if "longa" in m:
        return longa
    n = re.search(r"(\d+(?:[.,]\d+)?)\s*s", m)
    return float(n.group(1).replace(",", ".")) if n else curta


def ler_roteiro(caminho, curta=1.5, longa=12.0):
    """Lista de itens: ("secao", título) | ("texto", parágrafo) | ("pausa", segundos)."""
    caminho = Path(caminho)
    linhas = caminho.read_text(encoding="utf-8-sig").splitlines()
    md = caminho.suffix.lower() == ".md"
    if md:
        ini = next((i for i, l in enumerate(linhas) if l.lstrip().startswith("#") and INICIO.search(l)), None)
        if ini is None:
            sys.exit("Não achei no roteiro um título com a palavra ABERTURA. Coloque esse título onde a narração começa, "
                     "ou salve só o texto narrado num arquivo .txt e use esse arquivo.")
        linhas = linhas[ini:]
    itens = []
    for l in linhas:
        s = l.strip()
        if md and s.startswith("#"):
            titulo = s.lstrip("#").strip()
            if FIM.search(titulo) and itens:
                break
            itens.append(("secao", titulo))
            continue
        if not s or s.startswith(("🎞", ">", "|", "- ", "* ", "+ ", "---", "<!--")) or re.match(r"^\d+\.\s", s) and md:
            continue
        pos = 0
        for m in MARCA.finditer(s):
            antes = limpar(s[pos:m.start()])
            if antes:
                itens.append(("texto", antes))
            if m.group(1).strip().lower().startswith("pausa"):
                itens.append(("pausa", segundos_da_pausa(m.group(1), curta, longa)))
            pos = m.end()
        resto = limpar(s[pos:])
        if resto:
            itens.append(("texto", resto))
    return itens


def montar_trechos(itens, so_abertura=False):
    """Junta os parágrafos em trechos. Cada trecho termina numa pausa, num título ou no tamanho máximo.
    Devolve [{"texto", "pausa_depois"}]."""
    if so_abertura:
        secoes = [i for i, it in enumerate(itens) if it[0] == "secao"]
        if len(secoes) >= 2:
            itens = itens[:secoes[1]]
        elif not secoes:  # .txt: os primeiros parágrafos, até umas 60 palavras
            corte, palavras = [], 0
            for it in itens:
                corte.append(it)
                if it[0] == "texto":
                    palavras += len(it[1].split())
                    if palavras >= 60:
                        break
            itens = corte
    trechos, atual = [], []

    def fechar(pausa):
        if atual:
            trechos.append({"texto": "\n\n".join(atual), "pausa_depois": pausa})
            atual.clear()
        elif trechos and pausa:
            trechos[-1]["pausa_depois"] += pausa

    for tipo, valor in itens:
        if tipo == "texto":
            if atual and len("\n\n".join(atual)) + len(valor) > TAMANHO_MAX_TRECHO:
                fechar(0.0)
            atual.append(valor)
        elif tipo == "pausa":
            fechar(valor)
        elif tipo == "secao":
            fechar(0.0)
    fechar(0.0)
    if trechos and so_abertura:  # no roteiro inteiro a pausa final fica (ex.: a pausa longa do fim)
        trechos[-1]["pausa_depois"] = 0.0
    return trechos


def assinatura(texto, voz, velocidade):
    return hashlib.sha1(f"{voz}|{velocidade}|{texto}".encode("utf-8")).hexdigest()[:8]


# ------------------------------------------------------------------ áudio
def ffmpeg(*args):
    if not shutil.which("ffmpeg"):
        sys.exit("Falta o FFmpeg. A aula 0.7 instala com um prompt.")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, args)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"O FFmpeg falhou: {r.stderr.strip()[:400]}")


def duracao(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def mmss(s):
    s = int(round(s))
    return f"{s // 3600}h{s % 3600 // 60:02d}min{s % 60:02d}s" if s >= 3600 else f"{s // 60}min{s % 60:02d}s"


def juntar(trechos, pasta, saida, respiro):
    """Converte cada trecho para WAV igual, cria os silêncios e junta tudo num MP3."""
    tmp = pasta / "_juntar"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    lista = []
    for i, t in enumerate(trechos, 1):
        w = tmp / f"{i:03d}.wav"
        ffmpeg("-i", pasta / t["arquivo"], "-ar", 44100, "-ac", 1, "-c:a", "pcm_s16le", w)
        lista.append(w)
        pausa = t["pausa_depois"] if t["pausa_depois"] > 0 else (respiro if i < len(trechos) else 0)
        if pausa > 0:
            s = tmp / f"{i:03d}-silencio.wav"
            ffmpeg("-f", "lavfi", "-t", f"{pausa:.3f}", "-i", "anullsrc=r=44100:cl=mono", "-c:a", "pcm_s16le", s)
            lista.append(s)
    arq_lista = tmp / "lista.txt"
    caminho = lambda p: p.resolve().as_posix().replace("'", "'\\''")  # o FFmpeg lê os caminhos a partir da pasta da lista
    arq_lista.write_text("".join(f"file '{caminho(p)}'\n" for p in lista), encoding="utf-8")
    saida.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg("-f", "concat", "-safe", 0, "-i", arq_lista, "-c:a", "libmp3lame", "-q:a", 2, saida)
    shutil.rmtree(tmp, ignore_errors=True)
    return duracao(saida)


# ------------------------------------------------------------------ comandos
def cmd_chave(a):
    k, origem = chave()
    print(f"Chave encontrada em: {origem} ({len(k)} caracteres, terminando em ...{k[-4:]})")
    n, bruto = saldo()
    if n is None:
        print(f"A chave funcionou. Resposta do saldo: {bruto}")
    else:
        print(f"A chave funcionou. Saldo: {n:,.0f} créditos".replace(",", "."))


def cmd_vozes(a):
    r = pedir("GET", "/v3/voices", query={
        "provider": a.provider, "search": a.busca, "language": a.idioma, "gender": a.genero,
        "page_size": a.qtd, "page": a.pagina})
    dados = r.get("data", [])
    if not dados:
        print("Nenhuma voz com esse filtro. Tente outra busca, por exemplo --busca brazil ou --busca portuguese.")
    for x in dados:
        print(f"{x.get('voice_id')}\t{x.get('name')}\t{x.get('language') or ''}\t{x.get('gender') or ''}\t{x.get('preview_url') or 'sem prévia'}")
    pag = r.get("pagination") or {}
    if pag:
        print(f"\nPágina {pag.get('page')}, {len(dados)} vozes de {pag.get('total')} no total" + (" (tem mais: use --pagina)" if pag.get("has_more") else ""))


def gerar_trechos(pendentes, pasta, voz, velocidade):
    """Gera os trechos que faltam, até AO_MESMO_TEMPO por vez. Devolve os créditos gastos."""
    gasto, fila, rodando, feitos = 0.0, list(pendentes), {}, 0
    total = len(pendentes)
    while fila or rodando:
        while fila and len(rodando) < AO_MESMO_TEMPO:
            t = fila.pop(0)
            rodando[pedir_voz(t["texto"], voz, velocidade, Path(t["arquivo"]).stem)] = (t, 0)
        time.sleep(3)
        for tid in list(rodando):
            t, erros = rodando[tid]
            r = ver_tarefa(tid)
            st = r.get("status")
            if st == "done":
                url = (r.get("metadata") or {}).get("audio_url")
                if not url:
                    sys.exit(f"O ai33 terminou o trecho {t['n']} sem devolver o áudio: {r}")
                baixar(url, pasta / t["arquivo"])
                gasto += float(r.get("credit_cost") or 0)
                feitos += 1
                del rodando[tid]
                print(f"  trecho {t['n']:>3} pronto ({feitos}/{total})", flush=True)
            elif st == "error":
                del rodando[tid]
                if erros >= 1:
                    sys.exit(f"O trecho {t['n']} falhou duas vezes: {r.get('error_message')}. "
                             "Os trechos prontos ficaram guardados; rode de novo para continuar.")
                print(f"  trecho {t['n']} falhou ({r.get('error_message')}); tentando de novo", flush=True)
                rodando[pedir_voz(t["texto"], voz, velocidade, Path(t["arquivo"]).stem)] = (t, erros + 1)
    return gasto


def cmd_roteiro(a):
    roteiro = Path(a.roteiro)
    if not roteiro.exists():
        sys.exit(f"Não achei o roteiro {roteiro}.")
    trechos = montar_trechos(ler_roteiro(roteiro, a.pausa, a.pausa_longa), a.so_abertura)
    if not trechos:
        sys.exit("Não sobrou texto para narrar. Confira se o roteiro tem o texto narrado depois do título ABERTURA.")
    nome = roteiro.stem + ("-abertura" if a.so_abertura else "")
    saida = Path(a.saida) if a.saida else Path("audios") / f"{nome}.mp3"
    pasta = saida.parent / f".partes-{roteiro.stem}"
    voz = a.voz or "(escolha a voz)"
    for i, t in enumerate(trechos, 1):
        t["n"] = i
        t["arquivo"] = f"{i:03d}-{assinatura(t['texto'], voz, a.velocidade)}.mp3"
    refazer = set(a.refazer or [])
    pendentes = [t for t in trechos if t["n"] in refazer or not (pasta / t["arquivo"]).exists()]
    chars_total = sum(len(t["texto"]) for t in trechos)
    chars_gerar = sum(len(t["texto"]) for t in pendentes)
    custo = round(chars_gerar * CREDITOS_POR_CARACTERE)
    pausas = sum(1 for t in trechos if t["pausa_depois"] > 0)
    palavras = sum(len(t["texto"].split()) for t in trechos)

    print(f"Roteiro: {roteiro}" + ("  (só a abertura)" if a.so_abertura else ""))
    print(f"Texto narrado: {palavras} palavras, {chars_total} caracteres, {len(trechos)} trechos, {pausas} pausas")
    print(f"Duração estimada: {mmss(palavras / 150 * 60 / max(a.velocidade, 0.5) + sum(t['pausa_depois'] for t in trechos))} "
          f"(150 palavras por minuto na velocidade 1)")
    print(f"A gerar agora: {len(pendentes)} trechos, {chars_gerar} caracteres = cerca de {custo} créditos (estimativa: {CREDITOS_POR_CARACTERE} crédito por caractere)")

    if a.ver:
        print("\nComeço do texto:\n  " + trechos[0]["texto"][:300].replace("\n", "\n  "))
        print("\nFim do texto:\n  " + trechos[-1]["texto"][-300:].replace("\n", "\n  "))
        print("\nSimulação: nada foi gerado e nenhum crédito foi gasto.")
        return
    if not a.voz:
        sys.exit("Falta a voz. Liste as vozes com o comando vozes, ouça as prévias e passe --voz com o código da escolhida.")
    if custo > LIMITE_SEM_APROVACAO and not a.pode_gastar:
        sys.exit(f"Isso vai gastar cerca de {custo} créditos. Mostre esse número para a pessoa e, "
                 "depois que ela aprovar, rode de novo com --pode-gastar.")
    if pendentes:
        n, _ = saldo()
        if n is not None:
            print(f"Saldo antes: {n:,.0f} créditos".replace(",", "."))
            if n < custo:
                sys.exit(f"O saldo ({n:.0f}) não cobre os {custo} créditos estimados. Compre créditos e rode de novo.")
        pasta.mkdir(parents=True, exist_ok=True)
        print(f"Gerando {len(pendentes)} trechos com a voz {a.voz}, velocidade {a.velocidade}...", flush=True)
        gasto = gerar_trechos(pendentes, pasta, a.voz, a.velocidade)
    else:
        gasto = 0.0
        print("Todos os trechos já estavam prontos: nenhum crédito gasto.")

    (pasta / "partes.json").write_text(json.dumps({
        "roteiro": str(roteiro), "saida": str(saida), "voz": a.voz, "velocidade": a.velocidade,
        "trechos": trechos}, ensure_ascii=False, indent=1), encoding="utf-8")
    dur = juntar(trechos, pasta, saida, a.respiro)
    print(f"\nPronto: {saida}")
    print(f"Duração: {mmss(dur)} | trechos: {len(trechos)} | gerados agora: {len(pendentes)} | créditos gastos agora: {gasto:,.0f}".replace(",", "."))
    print(f"Os trechos ficaram em {pasta} (para refazer um trecho sem gerar tudo de novo).")


def normalizar(texto):
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9]+", t)


def cmd_conferir(a):
    roteiro = Path(a.roteiro)
    base = Path(a.saida).parent if a.saida else Path("audios")
    arq = base / f".partes-{roteiro.stem}" / "partes.json"
    if not arq.exists():
        sys.exit(f"Não achei {arq}. Gere a narração primeiro com o comando roteiro.")
    dados = json.loads(arq.read_text(encoding="utf-8"))
    pasta = arq.parent
    try:
        import numpy as np
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("Falta o faster-whisper. A aula 0.8 instala com um prompt.")
    print(f"Conferindo {len(dados['trechos'])} trechos com o Whisper (sem placa de vídeo, demora mais ou menos o tempo do áudio)...", flush=True)
    modelo = WhisperModel(a.modelo, device="cpu", compute_type="int8")
    ruins = []
    for t in dados["trechos"]:
        bruto = subprocess.run(["ffmpeg", "-v", "error", "-i", str(pasta / t["arquivo"]), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                               capture_output=True, check=True).stdout
        segs, _ = modelo.transcribe(np.frombuffer(bruto, dtype=np.float32), language=a.idioma, vad_filter=True)
        ouvido = " ".join(s.text for s in segs)
        nota = difflib.SequenceMatcher(None, normalizar(t["texto"]), normalizar(ouvido)).ratio()
        marca = "ok" if nota >= a.minimo else "REFAZER"
        print(f"  trecho {t['n']:>3}: {nota:5.0%}  {marca}", flush=True)
        if nota < a.minimo:
            ruins.append((t["n"], nota, t["texto"][:90].replace("\n", " "), ouvido.strip()[:90]))
    print()
    if not ruins:
        print(f"Tudo conferido: os {len(dados['trechos'])} trechos batem com o roteiro (mínimo {a.minimo:.0%}).")
        return
    print(f"{len(ruins)} trecho(s) abaixo de {a.minimo:.0%}. Ouça antes de refazer: nomes próprios e números às vezes só são escritos diferente.")
    for n, nota, esperado, ouvido in ruins:
        print(f"  trecho {n} ({nota:.0%})\n    roteiro: {esperado}\n    ouvido:  {ouvido}")
    print(f"\nPara refazer só esses: python ai33_tts.py roteiro {roteiro} --voz {dados['voz']} --velocidade {dados['velocidade']} --refazer "
          + " ".join(str(n) for n, *_ in ruins))


def cmd_falar(a):
    texto = a.texto if a.texto else Path(a.arquivo).read_text(encoding="utf-8").strip()
    if len(texto) * CREDITOS_POR_CARACTERE > LIMITE_SEM_APROVACAO and not a.pode_gastar:
        sys.exit(f"Isso vai gastar cerca de {round(len(texto) * CREDITOS_POR_CARACTERE)} créditos. Depois que a pessoa aprovar, rode de novo com --pode-gastar.")
    saida = Path(a.saida)
    tid = pedir_voz(texto, a.voz, a.velocidade, saida.stem)
    while True:
        time.sleep(3)
        r = ver_tarefa(tid)
        if r.get("status") == "done":
            baixar((r.get("metadata") or {})["audio_url"], saida)
            print(f"Pronto: {saida} ({mmss(duracao(saida))}, {r.get('credit_cost')} créditos)")
            return
        if r.get("status") == "error":
            sys.exit(f"O ai33 não conseguiu gerar: {r.get('error_message')}")


def main():
    ap = argparse.ArgumentParser(description="Narração com voz de IA pelo ai33.pro", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("chave", help="confere a chave e mostra os créditos")

    v = sub.add_parser("vozes", help="lista vozes com o link da prévia")
    v.add_argument("--provider", default="elevenlabs", help="elevenlabs, minimax, edge, kokoro, fishaudio...")
    v.add_argument("--busca", default="")
    v.add_argument("--idioma", default="")
    v.add_argument("--genero", default="", help="male ou female")
    v.add_argument("--qtd", type=int, default=30)
    v.add_argument("--pagina", type=int, default=1)

    r = sub.add_parser("roteiro", help="narra um roteiro inteiro (ou só a abertura)")
    r.add_argument("roteiro")
    r.add_argument("--voz")
    r.add_argument("--velocidade", type=float, default=1.0, help="de 0.5 a 1.5; história para dormir fica boa em 0.9")
    r.add_argument("--saida", help="padrão: audios/NOME-DO-ROTEIRO.mp3")
    r.add_argument("--so-abertura", action="store_true")
    r.add_argument("--ver", action="store_true", help="só mostra o que seria feito e o custo")
    r.add_argument("--pode-gastar", action="store_true", help="a pessoa já aprovou o gasto")
    r.add_argument("--refazer", type=int, nargs="+", metavar="N", help="números dos trechos a gerar de novo")
    r.add_argument("--pausa", type=float, default=1.5, help="segundos de cada [pausa]")
    r.add_argument("--pausa-longa", type=float, default=12.0, help="segundos de cada [pausa longa]")
    r.add_argument("--respiro", type=float, default=0.35, help="silêncio entre trechos sem [pausa]")

    c = sub.add_parser("conferir", help="confere a narração com o Whisper")
    c.add_argument("roteiro")
    c.add_argument("--saida", help="o mesmo --saida usado no comando roteiro, se você usou")
    c.add_argument("--minimo", type=float, default=0.85, help="nota mínima de cada trecho (0 a 1)")
    c.add_argument("--modelo", default=MODELO_WHISPER)
    c.add_argument("--idioma", default="pt")

    f = sub.add_parser("falar", help="narra um texto curto")
    f.add_argument("--voz", required=True)
    g = f.add_mutually_exclusive_group(required=True)
    g.add_argument("--texto")
    g.add_argument("--arquivo")
    f.add_argument("--saida", required=True)
    f.add_argument("--velocidade", type=float, default=1.0)
    f.add_argument("--pode-gastar", action="store_true")

    a = ap.parse_args()
    vel = getattr(a, "velocidade", None)
    if vel is not None and not 0.5 <= vel <= 1.5:
        sys.exit("A velocidade vai de 0.5 a 1.5.")
    {"chave": cmd_chave, "vozes": cmd_vozes, "roteiro": cmd_roteiro, "conferir": cmd_conferir, "falar": cmd_falar}[a.cmd](a)


if __name__ == "__main__":
    main()
