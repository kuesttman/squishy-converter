# Prompt Mestre para Geração do Sistema "Nebula"

**Contexto:**
Você é um Arquiteto de Software Sênior e Desenvolvedor Full-Stack especialista em Python (FastAPI) e React (Moderno). Eu preciso que você construa um sistema completo do zero chamado **"Nebula Media Hub"**.

**Objetivo:**
Crie uma aplicação web para gerenciamento e transcodificação de mídia (vídeo) focada em simplicidade visual e poder de processamento. O sistema substituirá softwares antigos e deve ser "Docker-first".

**Documentação de Referência:**
Eu preparei especificações detalhadas em arquivos separados (Visão Geral, Requisitos, Funcionalidades, Layout). Por favor, leia atentamente os requisitos abaixo baseados nesses documentos:

1.  **Nome e Estilo**: O sistema chama-se **Nebula**. Use uma paleta de cores "espacial" (Roxo Profundo, Azul Neon, Ciano) e Dark Mode nativo. Use componentes modernos (Shadcn/UI).
2.  **Stack Técnica**:
    *   **Backend**: Python FastAPI (Async), SQLModel (SQLite), FFmpeg.
    *   **Frontend**: React (Vite), TypeScript, TailwindCSS, Zustand.
    *   **Deploy**: Docker Compose único orquestrando tudo.
3.  **Funcionalidade Principal**:
    *   Escanear pastas de mídia locais.
    *   Permitir que o usuário configure "Versões de Saída" (Ex: Gerar 1080p e 720p do mesmo filme).
    *   Transcodificar usando FFmpeg (com suporte a NVENC/GPU).
    *   Dashboard em Tempo Real via WebSockets.
4.  **Idioma**: Todo o código, comentários e Interface do Usuário devem ser em **Português (Brasil)** ou ter suporte nativo a i18n configurado para PT-BR padrão.

**Sua Missão Agora:**
Gere a estrutura inicial do projeto, os arquivos de configuração (Docker, Poetry/Requirements, package.json) e o código fonte base para o Backend (FastAPI) e Frontend (React) que atenda a esses requisitos. Comece criando a estrutura de pastas e os arquivos de configuração vitais.

Seja criativo no design e rigoroso na qualidade do código Python.
