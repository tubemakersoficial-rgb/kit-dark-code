# Kit Dark Code

Skills, agentes, scripts e prompts do curso **Dark Code** (TubeMaker Academy): criar um canal dark no YouTube do zero, usando só o Claude Code.

Versão 0.1: cobre os módulos 0 (o app e o kit do canal), 2 (pesquisa), 3 (seu nicho) e o começo do 4 (roteiro).

## Como instalar

Abra uma sessão no Claude Code (aba Code do app Claude), cole o prompt do arquivo [INSTALAR.md](INSTALAR.md) e envie. O Claude baixa o kit, mostra o que vai instalar e copia as skills e os agentes.

Ou, no terminal, dentro da pasta do kit:

```bash
python instalar.py
```

O instalador só copia arquivos de texto para a pasta `.claude` do seu usuário. Ele não instala programas, não pede senha e não apaga nada: se já existir uma skill com o mesmo nome, a antiga é guardada com `.antigo`.

## O que vem no kit

14 skills, 5 agentes, 3 scripts, 3 modelos e 23 prompts das aulas. A lista completa, com a aula de cada um, está no [MAPA.md](MAPA.md).

| Skill | O que faz |
|---|---|
| `/pasta-do-canal` | Organiza a pasta do canal e cria o CLAUDE.md |
| `/checkup-kit` | Testa as ferramentas e mostra o que funciona |
| `/primeiro-video` | Um vídeo de 1 minuto completo, só com ferramentas grátis |
| `/nichos-virais` | 10 nichos crescendo, com nota e análise dos 3 melhores |
| `/concorrentes` | Compara 4 canais e acha o espaço vazio |
| `/outliers` | Vídeos do mês que estouraram e o padrão deles |
| `/titulos-thumbs` | 3 fórmulas de título e checklist de thumbnail |
| `/validar-nicho` | Nota e decisão: começar, ajustar ou trocar |
| `/meu-nicho` | Do nicho que você já tem até as 10 primeiras ideias |
| `/roteiro-dark` | Roteiro com fatos conferidos e mapa de retenção |
| `/revisar-roteiro` | Revisão de editor, com a tabela do que mudou |
| `/voz-gratis` | Narração grátis com Edge-TTS |
| `/legendas` | Legenda .srt com o Whisper |
| `/ajuda-dark-code` | Tira dúvidas do curso e do kit |

## Do que você precisa

- O app Claude com a aba Code (plano Pro ou Max).
- Python, Git, Node.js e FFmpeg. As aulas 0.6 a 0.9 instalam tudo com um prompt.
- Para as skills de pesquisa: o navegador do app Claude.

## Regras do kit

As skills seguem as mesmas regras das aulas: só números vistos na tela ou com fonte, nada de copiar títulos e roteiros de outros canais, e nenhuma instalação sem perguntar antes.

## Motion graphics

A skill `claude-video`, usada nas aulas 0.10 e 1.6, é de outro autor e não vem neste kit. A aula 0.10 mostra como instalar pelo repositório dela.
