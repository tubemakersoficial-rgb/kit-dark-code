---
name: legendas
description: Transcreve um áudio ou vídeo com o Whisper no computador da pessoa e cria a legenda .srt sincronizada. Use quando a pessoa pedir legenda, transcrição ou rodar /legendas com o arquivo.
---

# Legendas (aulas 0.8 e 4.4)

1. Confira se o Whisper (`faster-whisper`) e o FFmpeg estão instalados. Se faltar algo, diga o comando e peça confirmação antes de instalar. Na primeira vez o modelo é baixado e pode demorar alguns minutos.
2. Rode `ferramentas/legendar.py <áudio>` (ou o script do kit em `~/.claude/dark-code/scripts/`). O `.srt` sai ao lado do áudio.
3. Se existir o roteiro do vídeo, compare a legenda com ele e corrija nomes próprios, siglas e palavras erradas.
4. Mostre as primeiras legendas com os tempos e diga quantas são.
5. Avise: sem placa de vídeo a transcrição é mais lenta (cerca de 1,5 vez a duração do áudio).

## Regras que valem sempre

- Fale em português do Brasil, em linguagem simples, sem jargão.
- Só use números que você viu na tela ou numa fonte que você cita. O que for estimativa, escreva "estimativa".
- Se não tiver certeza, diga. Se não achar, diga quantos achou. Nunca invente.
- Não copie títulos, roteiros nem thumbnails de outros canais: use como referência e crie algo novo.
- Não crie contas, não faça login, não clique em anúncios e não compre nada.
- Não instale programas nem rode arquivos baixados da internet sem perguntar antes.
- Antes de começar, leia o `CLAUDE.md` da pasta do canal, se existir, e siga o que estiver lá.
- No fim, diga o que foi feito, onde está o arquivo e o que ficou sem conferir.
