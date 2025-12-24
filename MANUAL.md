# Manual Técnico do Squishy Converter

Este documento explica como o sistema Squishy funciona internamente, com foco no processo de conversão, gerenciamento de arquivos de mídia e estrutura do código.

## 1. Visão Geral da Arquitetura

O Squishy atua como uma interface intermediária entre seus servidores de mídia (Jellyfin/Plex) e o software de transcodificação (FFmpeg).

### Fluxo de Trabalho Principal:
1.  **Scanner (`scanner.py`):** O sistema conecta-se ao Jellyfin ou Plex para ler a biblioteca de mídia.
2.  **Interface Web (`app.py`):** O usuário seleciona um arquivo e escolhe um "Preset" (predefinição).
3.  **Gerenciador de Tarefas (`transcoder.py`):** Cria um "Job" (tarefa) e o coloca em uma fila de processamento.
4.  **Wrapper FFmpeg (`effeffmpeg/effeffmpeg.py`):** Constrói e executa o comando FFmpeg real para converter o arquivo.

## 2. Processo de Conversão (Como funciona a mágica)

A parte mais crítica do sistema reside no diretório `squishy/effeffmpeg/`.

### Como o comando FFmpeg é gerado?
A função `generate_ffmpeg_command` no arquivo `effeffmpeg.py` é responsável por montar a linha de comando que será executada. Ela toma decisões baseadas em:
- **Preset Escolhido:** Define codec de vídeo (ex: HEVC), codec de áudio (ex: AAC), resolução e qualidade.
- **Capacidades de Hardware:** O sistema detecta automaticamente se sua GPU suporta aceleração (via VAAPI) e adiciona as flags necessárias (`-hwaccel vaapi`, `-vf format=nv12,hwupload`, etc.).

### Áudio e Legendas (Comportamento Padrão)
Analisando o código atual (`effeffmpeg.py`), o sistema **não** instrui explicitamente o FFmpeg a copiar todos os fluxos (streams) do arquivo original.

- **Comportamento Observado:** O comando gerado não utiliza flags como `-map 0` (que copiaria tudo).
- **Consequência:** O FFmpeg usará seu comportamento padrão de seleção de streams:
    - **Vídeo:** Seleciona o "melhor" stream de vídeo (geralmente o de maior resolução/bitrate).
    - **Áudio:** Seleciona o "melhor" stream de áudio (geralmente o padrão ou com mais canais). O restante é descartado.
    - **Legendas:** Por padrão, o FFmpeg **ignora** legendas durante a transcodificação, a menos que instruído explicitamente. **Portanto, na versão atual do código, legendas provavelmente são perdidas no arquivo convertido.**

### Presets (Predefinições)
Os presets estão definidos em `config.py` (ou `config.json`) e controlam:
- `codec`: Codec de vídeo (h264, hevc, vp9).
- `scale`: Resolução alvo (1080p, 720p).
- `crf` ou `bitrate`: Controle de qualidade.
- `audio_codec`: Codec de áudio (aac, opus).

## 3. Funções Principais no Código

Para quem deseja modificar o comportamento, aqui estão as funções chave:

| Arquivo | Função | Responsabilidade |
| :--- | :--- | :--- |
| `squishy/transcoder.py` | `transcode(...)` | Gerencia o ciclo de vida do job, atualiza progresso e cria o arquivo sidecar `.json` ao final. |
| `effeffmpeg/effeffmpeg.py` | `generate_ffmpeg_command(...)` | **Coração da conversão.** Constrói a lista de argumentos para o FFmpeg. É aqui que você adicionaria `-map 0` para manter todos os áudios/legendas. |
| `effeffmpeg/effeffmpeg.py` | `detect_capabilities(...)` | Testa se o hardware suporta codificação via GPU. |

## 4. Hardware Acceleration (Aceleração de Hardware)
O sistema prioriza o uso de hardware. Se a aceleração falhar ou não estiver disponível (e o preset permitir fallback), ele reverterá automaticamente para codificação via software (CPU), que é muito mais lenta mas garante que o job termine.
