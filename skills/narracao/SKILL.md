---
name: narracao
description: Narra um roteiro com voz de IA pelo ai33 (vozes do ElevenLabs) - confere a chave sem mostrar, lista vozes com prévia, testa na abertura e só narra o roteiro inteiro depois do sim da pessoa, conferindo cada trecho com o Whisper. Use quando a pessoa pedir narração com IA, voz paga, voz do ai33 ou rodar /narracao com o roteiro.
---

# Narração com IA (aula 4.3)

Narra o roteiro com uma voz de IA pelo ai33.pro e só gasta créditos com o roteiro inteiro depois do sim da pessoa.

O script é `ferramentas/ai33_tts.py`, na pasta do canal. Se não estiver lá, copie de `~/.claude/dark-code/scripts/ai33_tts.py`. Rode sempre a partir da pasta do canal. `python ferramentas/ai33_tts.py --help` mostra todos os comandos.

## A chave

- A chave fica no arquivo `ai33_key.txt` da pasta de usuário da pessoa (ou na variável `AI33_API_KEY`). Quem lê a chave é o script.
- Nunca peça a chave na conversa. Nunca abra, leia, mostre nem copie esse arquivo, e nunca escreva a chave em outro lugar.
- Se a pessoa colar a chave na conversa, não use. Peça para ela salvar a chave no arquivo e, se o ai33 permitir, trocar por uma chave nova, porque a colada ficou no histórico.
- Se a chave faltar, explique o caminho e espere: entrar no ai33.pro, abrir **API Document** no menu da esquerda, clicar no botão de copiar ao lado de **API Key**, abrir o Bloco de Notas, colar e salvar na pasta de usuário com o nome `ai33_key.txt`, tipo **Documentos de texto**. A chave só aparece depois de comprar créditos.

## Passos

1. Rode `python ferramentas/ai33_tts.py chave`. Ele confere a chave e mostra o saldo.
2. Leia o `CLAUDE.md`. Se o campo **Voz** já tiver uma voz do ai33 (um código como `elevenlabs_...`), use essa voz, diga qual é e pule para o passo 4.
3. Liste as vozes com `vozes --busca portuguese --genero male` (troque pelo que a pessoa pediu: `female`, outro idioma). Se vierem poucas, tente `--busca brazil` e `--busca brasil`. Mostre 5 numa tabela: nome, código, gênero e o link da prévia. **Não escolha pela pessoa:** peça para ela ouvir as prévias e espere a resposta.
4. Rode `roteiro ROTEIRO.md --ver`. Mostre o começo e o fim do texto narrado, o número de trechos e de pausas e a estimativa de créditos. Se aparecer no texto algo que não é para narrar (título, nota, fonte, tabela), pare e avise antes de gastar.
5. Gere só a abertura: `roteiro ROTEIRO.md --voz CÓDIGO --velocidade V --so-abertura`. Velocidade 1 é a normal; "um pouco mais lenta" é 0.9; história para dormir fica boa entre 0.85 e 0.9. Diga o custo e onde está o arquivo, e peça para a pessoa ouvir.
6. Espere um sim claro. Mostre a estimativa do roteiro inteiro e o saldo, e só então rode `roteiro ROTEIRO.md --voz CÓDIGO --velocidade V --pode-gastar`, com a mesma voz e a mesma velocidade da abertura (os trechos da abertura são reaproveitados). Um roteiro de 30 minutos leva de 10 a 30 minutos: rode em segundo plano e avise a pessoa.
7. Confira com `conferir ROTEIRO.md`. Demora mais ou menos o tempo do áudio, então rode em segundo plano também. Para cada trecho abaixo da nota mínima, compare o que o roteiro diz com o que o Whisper ouviu:
   - diferença só na grafia de nomes ou números: não refaça, só avise;
   - palavras faltando, repetidas ou trocadas: ofereça refazer com `--refazer N`, dizendo quantos créditos gasta, e espere o sim.
8. Se a pessoa disser que uma palavra saiu com a pronúncia errada, proponha escrever essa palavra no roteiro do jeito que se fala e rodar de novo. Só o trecho que mudou é gerado outra vez.
9. Anote no campo **Voz** do `CLAUDE.md`: `ai33 · NOME (CÓDIGO) · velocidade V`. Se já tinha outra voz anotada, pergunte antes de trocar.
10. No fim, mostre: o arquivo, a duração, os créditos gastos, o saldo depois e o que ficou sem conferir.

## Cuidados

- O custo é uma estimativa: cada caractere gasta cerca de 1,1 crédito, e o script calcula com um pouco de folga. Nunca narre o roteiro inteiro sem o sim da pessoa, e nunca compre créditos.
- Não diga que o uso comercial está liberado. Diga para a pessoa ler os termos de uso do ai33 antes de monetizar.
- Não apague a pasta `audios/.partes-NOME/` até o vídeo estar pronto: é ela que permite refazer um trecho sem gastar com o resto.

## Regras que valem sempre

- Fale em português do Brasil, em linguagem simples, sem jargão.
- Só use números que você viu na tela ou numa fonte que você cita. O que for estimativa, escreva "estimativa".
- Se não tiver certeza, diga. Se não achar, diga quantos achou. Nunca invente.
- Não copie títulos, roteiros nem thumbnails de outros canais: use como referência e crie algo novo.
- Não crie contas, não faça login, não clique em anúncios e não compre nada.
- Não instale programas nem rode arquivos baixados da internet sem perguntar antes.
- Antes de começar, leia o `CLAUDE.md` da pasta do canal, se existir, e siga o que estiver lá.
- No fim, diga o que foi feito, onde está o arquivo e o que ficou sem conferir.
