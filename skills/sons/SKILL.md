---
name: sons
description: Coloca música de fundo e sons de ambiente por baixo da narração, só com sons de origem e licença conhecidas - sugere o que buscar, confere cada arquivo, mistura no volume certo com a música abaixando quando a voz fala e escreve o arquivo de créditos. Use quando a pessoa pedir trilha, música de fundo, efeitos, som de ambiente ou rodar /sons.
---

# Música e efeitos (aula 4.7)

Coloca música de fundo e sons de ambiente por baixo da narração, sem risco de direitos autorais.

O script é `ferramentas/trilha.py`, na pasta do canal. Se não estiver lá, copie de `~/.claude/dark-code/scripts/trilha.py`. `python ferramentas/trilha.py --help` mostra tudo.

## Onde a pessoa baixa, do mais seguro ao que pede cuidado

| Fonte | Pode monetizar? | Crédito na descrição | Começo do nome do arquivo |
|---|---|---|---|
| Biblioteca de áudio do YouTube (YouTube Studio, menu da esquerda, ou youtube.com/audiolibrary) | Sim. O YouTube diz que as faixas de lá não são reivindicadas pelo Content ID | Só nas faixas Creative Commons; o filtro "Atribuição não é necessária" evita isso | `youtube-` |
| Freesound (precisa de conta para baixar) | Licença zero e atribuição: sim. Atribuição não comercial: **não** | Zero: não. Atribuição: sim, com o autor e o link do som | `freesound-cc0-` ou `freesound-by-` |
| Pixabay | Sim, pela licença do Pixabay | Não é obrigatório | `pixabay-` |
| Flow Music, do Google | O Google lista uso comercial só nos planos pagos | Não | `flowmusic-pago-` |

- No Pixabay há relatos de músicas registradas no Content ID. Se a pessoa usar uma música de lá, peça para baixar também o certificado de licença.
- No Freesound, um som pode cair no Content ID quando alguém o usou numa música registrada. Dá para contestar.
- Nunca use música de outros vídeos, de canais "sem copyright", de filmes, novelas ou músicas famosas.

## Passos

1. Leia o roteiro e o `CLAUDE.md`. Sugira: o clima da música (instrumento, ritmo, sem batida forte e sem voz cantada, para não brigar com a narração), dois ou três sons de ambiente que combinam com as cenas e palavras para buscar, em português e em inglês.
2. Peça para a pessoa baixar e salvar em `audios/trilha/`, com o começo do nome dizendo a fonte (tabela acima). **Você não baixa nada e não faz login** em nenhum desses sites.
3. Rode `trilha.py conferir audios/trilha/`. Se aparecer arquivo de origem desconhecida ou de licença não comercial, pare e pergunte. Se uma faixa do YouTube for Creative Commons, peça o texto de crédito copiado do ícone de licença da Biblioteca.
4. Misture: `trilha.py mixar --voz NARRAÇÃO --musica MÚSICA --ambiente SOM1 SOM2 --saida audios/NOME-com-trilha.mp3`. O padrão é a música 18 dB abaixo da voz (e uns 7 dB mais baixa enquanto a voz fala), cada ambiente 26 dB abaixo e o volume final em -14 LUFS. Para história para dormir, `--lufs -16` deixa tudo mais calmo. A narração original nunca é alterada.
5. Mostre a tabela de volumes e peça para a pessoa ouvir. Música alta demais: `--musica-db 22`. Baixa demais: `--musica-db 15`. Para o ambiente, o mesmo com `--ambiente-db`.
6. Escreva `audios/trilha/creditos.md` com uma linha por arquivo: o arquivo, a fonte, a licença, o link (quando tiver), o texto de crédito (ou "não precisa") e a data. Diga quais créditos vão na descrição do vídeo.
7. Se a pessoa disser que o vídeo recebeu uma reivindicação: explique que reivindicação não é aviso de violação, que ela pode abrir os detalhes no YouTube Studio e contestar, e que o `creditos.md` (e o certificado, no caso do Pixabay) é a prova de onde o som veio.

## Cuidados

- As licenças mudam. Se a pessoa perguntar algo que não está aqui, confira a página oficial da fonte antes de responder.
- Você não é advogado: o que for dúvida jurídica, diga para confirmar na página oficial ou com um profissional.

## Regras que valem sempre

- Fale em português do Brasil, em linguagem simples, sem jargão.
- Só use números que você viu na tela ou numa fonte que você cita. O que for estimativa, escreva "estimativa".
- Se não tiver certeza, diga. Se não achar, diga quantos achou. Nunca invente.
- Não copie títulos, roteiros nem thumbnails de outros canais: use como referência e crie algo novo.
- Não crie contas, não faça login, não clique em anúncios e não compre nada.
- Não instale programas nem rode arquivos baixados da internet sem perguntar antes.
- Antes de começar, leia o `CLAUDE.md` da pasta do canal, se existir, e siga o que estiver lá.
- No fim, diga o que foi feito, onde está o arquivo e o que ficou sem conferir.
