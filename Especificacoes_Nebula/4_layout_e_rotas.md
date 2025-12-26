# Mapa de Navegação e Interface (UI/UX)

## Sitemap (Estrutura de Páginas)

### 1. **Login (`/login`)**
*   **Visual**: Fundo com blur da logo, card centralizado em vidro (glass).
*   **Inputs**: Senha (ou Usuário/Senha).
*   **Ação**: Entrar.

### 2. **Dashboard (`/`) - A "Home"**
*   **Header**: Logo Nebula, Status do Sistema (CPU/RAM/GPU Load), Seletor de Tema (Sol/Lua), Logout.
*   **Hero Section**:
    *   **Active Job**: Se houver algo rodando, mostrar em destaque grande com Banner do filme/série ao fundo e barra de progresso.
*   **Grid de Status**:
    *   "Na Fila": Número.
    *   "Concluídos Hoje": Número.
    *   "Economia Total": GBs.
*   **Últimas Atividades**: Lista compacta dos últimos 5 eventos.

### 3. **Biblioteca (`/library`)**
*   **Visual**: Grid de posteres (estilo Netflix/Jellyfin).
*   **Filtros**: "Não Processados", "Otimizados", "Erro".
*   **Ação em Card**: Hover mostra botão "Squish Now" (Processar Agora).

### 4. **Fila de Processamento (`/queue`)**
*   **Visual**: Lista detalhada.
*   **Colunas**: Mídia, Preset, Progresso, Estimativa, Ações (Pause/Delete).
*   **Features**: Drag & drop para mudar ordem.

### 5. **Configurações (`/settings`)**
*   **Abas Laterais**:
    *   **Geral**: Idioma, Tema, Portas.
    *   **Caminhos**: Mapeamento de pastas (`/media`).
    *   **Transcodificação**: Seleção de GPU, Presets, Multi-versão.
    *   **Integrações**: API Keys do Jellyfin/Plex/Sonarr.
    *   **Notificações**: Discord/Telegram Webhooks.

### 6. **Wizard de Instalação (`/setup`)**
*   Aparece apenas se `config.json` não existir.
*   Passo a passo amigável: "Bem-vindo ao Nebula. Vamos configurar sua mídia."

## Componentes Chave
*   **Toasts**: Notificações flutuantes no canto superior direito para sucesso/erro.
*   **Modais**: Para confirmações ("Deseja deletar o arquivo original?").
*   **Logs Viewer**: Um console acoplado na UI para ver logs do FFmpeg em tempo real (estilo terminal matrix).
