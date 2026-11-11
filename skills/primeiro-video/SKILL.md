---
name: primeiro-video
description: Faz um vídeo curto completo (cerca de 1 minuto) só com ferramentas grátis - roteiro com fatos conferidos, voz grátis, cenas no Remotion, legenda e montagem. Use quando a pessoa pedir o primeiro vídeo, um vídeo de teste do canal ou rodar /primeiro-video com o tema.
---

# Primeiro vídeo (aula 0.14)

Entrada: o tema do vídeo. Se a pessoa não disser, pergunte.

1. **Roteiro:** 1 minuto (cerca de 150 palavras), com gancho nos primeiros segundos e só fatos verdadeiros, conferidos na web. Salve em `roteiros/NNN-nome-do-video.md`, com as fontes no fim.
2. **Voz:** gere a narração com voz grátis (`ferramentas/voz_gratis.py`, Edge-TTS). Se a narração passar muito de 1 minuto, enxugue o texto sem perder os fatos e gere de novo.
3. **Cenas:** crie as cenas com o Remotion em estilo dark: fundo escuro, texto grande, movimento lento, uma cena por parte do roteiro. Siga o estilo visual do `CLAUDE.md`, se houver.
4. **Legenda:** `ferramentas/legendar.py` no áudio. Compare a legenda com o roteiro e corrija palavras erradas.
5. **Montagem:** vídeo 1920x1080 em `videos/NNN-nome-do-video.mp4`, com narração e legenda. Ajuste o volume para o padrão do YouTube (cerca de -14 LUFS).
6. **Conferência:** antes de abrir, tire alguns quadros do vídeo e confira texto, cores e legenda. Depois abra o vídeo para a pessoa assistir.

Use o mesmo nome base em todos os arquivos. Não use nada pago.

## Regras que valem sempre

- Fale em português do Brasil, em linguagem simples, sem jargão.
- Só use números que você viu na tela ou numa fonte que você cita. O que for estimativa, escreva "estimativa".
- Se não tiver certeza, diga. Se não achar, diga quantos achou. Nunca invente.
- Não copie títulos, roteiros nem thumbnails de outros canais: use como referência e crie algo novo.
- Não crie contas, não faça login, não clique em anúncios e não compre nada.
- Não instale programas nem rode arquivos baixados da internet sem perguntar antes.
- Antes de começar, leia o `CLAUDE.md` da pasta do canal, se existir, e siga o que estiver lá.
- No fim, diga o que foi feito, onde está o arquivo e o que ficou sem conferir.
