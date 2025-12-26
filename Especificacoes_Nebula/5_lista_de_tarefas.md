# Task List para o Desenvolvedor LLM

Use este checklist para guiar a geração do código.

## Fase 1: Setup e Fundações
- [ ] Criar estrutura de diretórios (`backend`, `frontend`, `docker`).
- [ ] Configurar `docker-compose.yml` com serviços `api`, `web`, `redis` (opcional).
- [ ] Backend: Setup inicial FastAPI, CORS, Configuração Pydantic.
- [ ] Backend: Configuração de Logger (Colorido e estruturado).
- [ ] Frontend: Setup Vite + React + TypeScript + TailwindCSS.
- [ ] Frontend: Instalar `shadcn/ui` e configurar tema base (Cores Nebula).

## Fase 2: Backend Core (A "Mente")
- [ ] Modelagem de Dados (SQLModel): `MediaItem`, `Job`, `User`, `Settings`.
- [ ] Criar Serviço de Scan (`ScannerService`): Varredura de diretórios recursiva.
- [ ] Criar Serviço de FFmpeg (`TranscoderService`): Wrapper para rodar comandos.
- [ ] API Endpoints:
  - `GET /api/media` (Listar filmes).
  - `POST /api/scan` (Gatilho manual).
  - `POST /api/queue` (Adicionar job).
  - `GET /api/status` (SSE/WebSocket para progresso).

## Fase 3: Frontend e UI (A "Cara")
- [ ] Criar Layout Base (Sidebar, Header).
- [ ] Página Dashboard: Consumir API de stats.
- [ ] Página Biblioteca: Grid de itens com paginação.
- [ ] Página Settings: Formulários controlados (React Hook Form).
- [ ] Implementar WebSocket Client para atualizar barras de progresso sem F5.

## Fase 4: Automação e Polimento
- [ ] Implementar Multi-versão (Loop no backend para gerar N jobs por arquivo).
- [ ] Implementar "Watchdog" ou Scheduler para scan automático.
- [ ] Testar integração com Docker (Passar GPU para o container).
- [ ] Escrever README.md detalhado de como rodar.
