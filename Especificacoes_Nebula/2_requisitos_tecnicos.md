# Requisitos Técnicos e Tecnologias

## 1. Stack Tecnológico (Recomendado)
Para garantir modernidade, performance e facilidade de manutenção (fugindo do "spaghetti code" antigo):

### Backend (A "Máquina")
*   **Linguagem**: **Python 3.11+**
*   **Framework API**: **FastAPI** (Assíncrono, Rápido, Auto-documentado com Swagger UI).
*   **Banco de Dados**: **SQLite** (com **SQLModel** ou **SQLAlchemy 2.0**) para simplicidade e portabilidade inicial. (Fácil migração para PostgreSQL se necessário).
*   **Gerenciamento de Dependências**: **Poetry** ou `pip-tools` (para evitar conflitos de versão).
*   **Transcodificação**: **FFmpeg** (via wrapper assíncrono ou subprocessos controlados).
*   **Tasks Assíncronas**: **ARQ** (Redis-backed) ou **FastAPI BackgroundTasks** (para começar simples) + Fila em memória/banco. Recomendado: Usar uma fila persistente simples baseada em SQLite para evitar dependência extra do Redis se o usuário quiser simplicidade.

### Frontend (A "Interface")
*   **Framework**: **React** (via **Vite**) ou **Next.js** (se SSR for desejado, mas Vite é mais leve para Single Page Apps).
*   **Linguagem**: **TypeScript** (Segurança e autocomplete, essencial para projetos médios/grandes).
*   **Estilização**: **TailwindCSS** (Padrão de mercado, rápido desenvolvimento) + **Shadcn/ui** (Componentes belíssimos pré-prontos que seguem o design "Premium").
*   **Estado Global**: **Zustand** ou **TanStack Query** (React Query) para gerenciar dados da API em tempo real.
*   **Comunicação Real-time**: **WebSocket** (Socket.io ou nativo do FastAPI) para barras de progresso ao vivo.
*   **Gráficos**: **Recharts** para estatísticas de uso.

## 2. Requisitos de Ambiente
*   **Docker**: O sistema deve ser totalmente "Dockerizado" (Dockerfile + docker-compose.yml).
*   **GPU Pass-through**: Configuração pronta para NVIDIA (NVENC) e Intel (QSV) no Docker Compose.
*   **Volumes**: Mapeamento claro de `/data`, `/config`, `/transcode-temp`.

## 3. Estrutura de Pastas Sugerida
```
nebula-media/
├── backend/            # API FastAPI
│   ├── app/
│   │   ├── api/        # Endpoints (Routes)
│   │   ├── core/       # Configs (Settings, Logging)
│   │   ├── models/     # SQLModel classes
│   │   ├── services/   # Lógica de Negócio (Transcoder, Scanner)
│   │   └── main.py     # Entrypoint
│   └── Dockerfile
├── frontend/           # React/Vite App
│   ├── src/
│   │   ├── components/ # Botões, Cards, Layouts
│   │   ├── pages/      # Views (Dashboard, Settings, Queue)
│   │   ├── hooks/      # Lógica de interface
│   │   └── lib/        # Utilitários (API Client)
│   └── Dockerfile
├── docker-compose.yml  # Orquestração
└── README.md
```

## 4. Requisitos Não-Funcionais
*   **Internacionalização (i18n)**: Todo o texto deve vir de arquivos de tradução (JSON), com suporte nativo a PT-BR e EN-US desde o dia 0.
*   **Responsividade**: Mobile-first. O painel deve ser controlável pelo celular.
*   **Dark Mode**: Padrão do sistema.
