# Squishy Media Manager - Task List

## Fase 1: Configuração Docker e Database
- [x] Criar `docker-compose.dev.yml` para build local
- [x] Configurar `config.json` com credenciais Jellyfin
- [x] Fix CRLF em `entrypoint.sh` no Dockerfile

## Fase 2: Migração para SQLite
- [x] Criar `squishy/database.py`
- [x] Refatorar `squishy/models.py` para SQLAlchemy
- [x] Configurar DB em `squishy/app.py`
- [x] Atualizar `squishy/transcoder.py` com funções de DB
- [x] Atualizar `squishy/blueprints/ui.py`
- [x] Atualizar `squishy/blueprints/api.py`
- [x] Atualizar `squishy/blueprints/library.py`
- [x] Adicionar `flask-sqlalchemy` ao `pyproject.toml`

## Fase 3: Funções Faltantes (CORRIGIDO)
- [x] `start_transcode()` - Inicia ou enfileira job
- [x] `cancel_job()` - Cancela job em andamento
- [x] `remove_job()` - Remove job do banco
- [x] `apply_output_path_mapping()` - Mapeamento de paths

## Fase 4: Build e Teste Local
- [ ] Executar `docker-compose -f docker-compose.dev.yml build`
- [ ] Executar `docker-compose -f docker-compose.dev.yml up -d`
- [ ] Verificar logs com `docker-compose -f docker-compose.dev.yml logs -f`
- [ ] Testar interface web em http://localhost:5000
- [ ] Testar conexão com Jellyfin
- [ ] Testar criação de job de transcodificação

## Fase 5: Próximos Passos (Após Testes)
- [ ] Implementar automação (Watcher, Hooks)
- [ ] Dashboard avançado
- [ ] Atualizar documentação
