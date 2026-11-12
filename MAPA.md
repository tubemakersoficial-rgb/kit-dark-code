# Mapa do Kit Dark Code (versão 0.2)

## Skills
Digite `/` numa sessão do Claude Code para ver a lista. Cada skill também é acionada quando você pede a tarefa com as suas palavras.

| Skill | Aula | O que faz |
|---|---|---|
| `/pasta-do-canal` | 0.3 | Organiza a pasta do canal e cria o CLAUDE.md |
| `/checkup-kit` | 0.13 | Testa as ferramentas e mostra o que funciona |
| `/primeiro-video` | 0.14 | Um vídeo de 1 minuto completo, só com ferramentas grátis |
| `/nichos-virais` | 2.1 | 10 nichos crescendo, com nota e análise dos 3 melhores |
| `/concorrentes` | 2.2 e 3.2 | Compara 4 canais e acha o espaço vazio |
| `/outliers` | 2.3 | Vídeos do mês que estouraram e o padrão deles |
| `/titulos-thumbs` | 2.4 | 3 fórmulas de título e checklist de thumbnail |
| `/validar-nicho` | 2.5 e 3.1 | Nota e decisão: começar, ajustar ou trocar |
| `/meu-nicho` | módulo 3 | Do nicho que você já tem até as 10 primeiras ideias |
| `/roteiro-dark` | 3.6 e 4.1 | Roteiro com fatos conferidos e mapa de retenção |
| `/revisar-roteiro` | 4.2 | Revisão de editor, com a tabela do que mudou |
| `/narracao` | 4.3 | Narração com voz de IA pelo ai33, testando na abertura antes de gastar |
| `/voz-gratis` | 0.14 e 4.5 | Narração grátis com Edge-TTS |
| `/legendas` | 0.8 e 4.4 | Legenda .srt com o Whisper |
| `/ajuda-dark-code` | 1.7 | Tira dúvidas do curso e do kit |

## Agentes
O Claude chama os agentes quando a tarefa pede. Você também pode pedir: "use o agente pesquisador para...".

| Agente | O que faz |
|---|---|
| `pesquisador` | Pesquisa nicho, concorrentes e fontes |
| `roteirista` | Escreve e reescreve roteiros no estilo do canal |
| `diretor-de-arte` | Prompts de imagem e thumbnails no mesmo estilo |
| `editor` | Monta o vídeo e confere o resultado |
| `fiscal-de-regras` | Confere direitos autorais e regras do YouTube antes de postar |

## Scripts (pasta `scripts/`)
| Script | O que faz |
|---|---|
| `legendar.py` | Transcreve um áudio com o Whisper e cria o `.srt` |
| `recortar.py` | Tira o fundo de imagens com o rembg |
| `voz_gratis.py` | Narração grátis com Edge-TTS |
| `ai33_tts.py` | Narração com voz de IA pelo ai33: vozes, abertura de teste, roteiro inteiro e conferência com o Whisper |

## Modelos (pasta `modelos/`)
| Arquivo | Para que serve |
|---|---|
| `CLAUDE.md` | A memória do canal, para preencher |
| `LEIA-ME.md` | O que vai em cada pasta do canal |
| `skill-do-seu-canal.md` | Modelo para criar a skill do seu canal (aula 1.5) |

## Prompts das aulas (pasta `prompts/`)
| Aula | Arquivo |
|---|---|
| 0.3 | `prompts/0-3-pasta-do-canal.md` |
| 0.5 | `prompts/0-5-kit-do-canal.md` |
| 0.6 | `prompts/0-6-instalar-a-base.md` |
| 0.7 | `prompts/0-7-ffmpeg.md` |
| 0.8 | `prompts/0-8-whisper.md` |
| 0.9 | `prompts/0-9-remotion.md` |
| 0.11 | `prompts/0-11-teste-do-chrome.md` |
| 0.12 | `prompts/0-12-kit-de-imagem.md` |
| 0.13 | `prompts/0-13-checkup.md` |
| 0.14 | `prompts/0-14-primeiro-video.md` |
| 2.1 | `prompts/2-1-nichos-virais.md` |
| 2.2 | `prompts/2-2-concorrentes.md` |
| 2.3 | `prompts/2-3-outliers.md` |
| 2.4 | `prompts/2-4-titulos-thumbs.md` |
| 2.5 | `prompts/2-5-validacao.md` |
| 3.1 | `prompts/3-1-ja-tenho-um-nicho.md` |
| 3.2 | `prompts/3-2-concorrentes-do-meu-nicho.md` |
| 3.3 | `prompts/3-3-angulo.md` |
| 3.4 | `prompts/3-4-identidade.md` |
| 3.5 | `prompts/3-5-dez-ideias.md` |
| 3.6 | `prompts/3-6-primeiro-roteiro.md` |
| 4.1 | `prompts/4-1-roteiro-que-prende.md` |
| 4.2 | `prompts/4-2-revisao.md` |
| 4.3 | `prompts/4-3-narracao-com-ia.md` |

## O que ainda vem
Imagens automáticas, montagem do vídeo, thumbnails, os formatos (histórias para dormir, banco de vídeos, palito, Shorts e outros), publicação e analytics entram nas próximas versões, junto com as aulas.
