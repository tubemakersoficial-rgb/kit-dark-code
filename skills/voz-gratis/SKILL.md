---
name: voz-gratis
description: Gera narração com voz grátis (Edge-TTS) a partir de um roteiro ou texto, para testar antes de assinar uma voz paga. Use quando a pessoa pedir narração grátis, voz de teste ou rodar /voz-gratis com o roteiro.
---

# Voz grátis (aulas 0.14 e 4.5)

1. Confira se o `edge-tts` está instalado (`python -m edge_tts --help`). Se não estiver, diga o comando (`pip install edge-tts`) e peça confirmação antes de instalar.
2. Tire do roteiro só o texto narrado (sem títulos, tabelas, fontes nem marcações).
3. Gere o áudio com `ferramentas/voz_gratis.py` (ou o script do kit em `~/.claude/dark-code/scripts/`). Vozes em português: `pt-BR-AntonioNeural` (masculina) e `pt-BR-FranciscaNeural` (feminina). Para narração calma, use `--velocidade -10%`.
4. Salve em `audios/` com o mesmo nome base do roteiro.
5. Diga a duração do áudio e compare com a duração planejada. Se passar muito, sugira onde enxugar.
6. Avise: a voz grátis serve para testar. Para o canal, vale usar sempre a mesma voz e anotar no `CLAUDE.md`.

## Regras que valem sempre

- Fale em português do Brasil, em linguagem simples, sem jargão.
- Só use números que você viu na tela ou numa fonte que você cita. O que for estimativa, escreva "estimativa".
- Se não tiver certeza, diga. Se não achar, diga quantos achou. Nunca invente.
- Não copie títulos, roteiros nem thumbnails de outros canais: use como referência e crie algo novo.
- Não crie contas, não faça login, não clique em anúncios e não compre nada.
- Não instale programas nem rode arquivos baixados da internet sem perguntar antes.
- Antes de começar, leia o `CLAUDE.md` da pasta do canal, se existir, e siga o que estiver lá.
- No fim, diga o que foi feito, onde está o arquivo e o que ficou sem conferir.
