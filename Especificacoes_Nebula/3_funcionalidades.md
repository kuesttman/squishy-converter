# Funcionalidades e Regras de Negócio

## 1. Gerenciamento de Mídia
*   **Scanner Inteligente**:
    *   Varredura manual e agendada (Cron).
    *   Detecção de novos arquivos baseada em hash (evitar re-processar renomeados).
    *   Ignorar arquivos por padrão (ex: `.sample`, `_SQUISHED`).
*   **Metadados**:
    *   Extração automática via `ffprobe` (Codecs, Bitrate, Duração, Resolução).
    *   Integração opcional com TMDB/Jellyfin para obter capas (Posters).

## 2. Motor de Transcodificação (The Core)
*   **Multi-Versão (A "Killer Feature")**:
    *   O usuário define "Perfis de Saída" (Ex: `Mobile 720p`, `TV 4K`, `Universal 1080p`).
    *   O sistema pode gerar TODAS as versões selecionadas para um arquivo de entrada.
*   **Lógica de Decisão**:
    *   "Se o arquivo original for HEVC, Copiar vídeo?" (Sim/Não).
    *   "Se o áudio for AAC, converter para AC3?"
*   **Hardware Acceleration**:
    *   Detecção automática de GPU (NVENC/QSV/VAAPI) na inicialização.
*   **Gestão de Arquivo Original**:
    *   Opções: `Manter`, `Mover para Pasta de Backup`, `Deletar`.
    *   Segurança: Só deletar após sucesso verificado e hash check da saída.

## 3. Automação
*   **Webhooks**: Endpoint `/api/webhook/trigger` para receber notificações do Sonarr/Radarr ("On Download Import").
*   **Watch Folders**: Monitoramento de pasta em tempo real (via `watchdog` library).

## 4. Interface e Dashboard
*   **Dashboard Ao Vivo**:
    *   Cards mostrando jobs ativos: "Filme X - 45% (Transcodificando...) - ETA 5 min".
    *   Gráfico de pizza: "Espaço em Disco" vs "Espaço Economizado".
*   **Fila de Jobs (Queue)**:
    *   Pausar, Cancelar, Retomar.
    *   Arrastar e soltar para reordenar prioridade.
    *   Botão "Retry Failed" (Tentar novamente falhados).
*   **Histórico**:
    *   Log completo de arquivos processados.
*   **Configurações**:
    *   Editor visual de Presets de FFmpeg (sem precisar escrever linha de comando na mão).

## 5. Sistema de Usuários
*   **Login Único (Admin)**: Proteção da interface web.
*   **Setup Inicial (Wizard)**: No primeiro acesso, perguntar:
    1.  Onde estão seus arquivos?
    2.  Qual a URL do Jellyfin?
    3.  Qual idioma deseja?
