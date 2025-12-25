# Análise do Projeto - Status e Próximos Passos

## Resumo do que foi implementado

### 1. Migração para SQLite (Parcialmente Completa)
- ✅ `squishy/database.py` - Módulo de inicialização do SQLAlchemy
- ✅ `squishy/models.py` - Modelos ORM (MediaItem, Movie, Episode, TVShow, TranscodeJob)
- ✅ `squishy/app.py` - Configuração do banco de dados
- ⚠️ `squishy/transcoder.py` - **INCOMPLETO** (faltam funções críticas)
- ✅ `squishy/blueprints/ui.py` - Atualizado para usar `get_all_jobs()`
- ✅ `squishy/blueprints/api.py` - Atualizado para usar `get_all_jobs()`
- ✅ `squishy/blueprints/library.py` - Removido uso do dicionário `MEDIA`
- ✅ `pyproject.toml` - Adicionado `flask-sqlalchemy`

### 2. Docker Setup
- ✅ `docker-compose.dev.yml` - Configurado para build local
- ✅ `Dockerfile` - Fix de line endings do `entrypoint.sh`
- ✅ `config/config.json` - Credenciais Jellyfin configuradas

---

## ⚠️ PROBLEMAS CRÍTICOS A RESOLVER

### Funções faltando em `transcoder.py`

O arquivo `squishy/blueprints/ui.py` importa estas funções que **NÃO EXISTEM** no `transcoder.py` atual:

```python
from squishy.transcoder import (
    create_job,           # ✅ EXISTE
    start_transcode,      # ❌ NÃO EXISTE
    apply_output_path_mapping,  # ❌ NÃO EXISTE
    remove_job as remove_transcode_job,  # ❌ NÃO EXISTE
    cancel_job as cancel_transcode_job,  # ❌ NÃO EXISTE
)

### Proposed Changes (Phase 3: Batch Operations)

### UI Changes
#### [MODIFY] [show_detail.html](file:///c:/Users/sk4rf/OneDrive/Documentos/Softwares/Repositorios/squishy-converter/squishy/templates/ui/show_detail.html)
- Add checkboxes to each episode row.
- Add "Select All / None" controls.
- Add "Squish Season" button in season headers.
- Add "Squish Show" button in main header.
- Add floating "Batch Action Bar" for selected items.

#### [NEW] [batch.js](file:///c:/Users/sk4rf/OneDrive/Documentos/Softwares/Repositorios/squishy-converter/squishy/static/js/batch.js)
- Handle selection logic (shift-click ranges, select all).
- Handle "Squish" button click -> Open Modal.
- Submit batch request to backend.

### Backend Changes
#### [MODIFY] [ui.py](file:///c:/Users/sk4rf/OneDrive/Documentos/Softwares/Repositorios/squishy-converter/squishy/blueprints/ui.py)
- New route `/batch/transcode` (POST).
- Accepts JSON: `{ media_ids: [...], preset_name: "..." }`.
- Iterates and creates jobs.
- Flashes summary ("Started X jobs").

## User Review Required
- The batch operation might queue many jobs. Ensure `max_concurrent_jobs` logic in backend is robust (it is).

## Verification Plan
- Select multiple episodes -> Squish -> Verify multiple jobs in Jobs tab.
- Squish Season -> Verify all episodes in season are queued.

### Funções a implementar:

1. **`start_transcode(job, media_item, preset_name, output_dir)`**
   - Inicia ou enfileira um job de transcodificação

2. **`cancel_job(job_id)`**
   - Cancela um job em andamento
   - Atualiza status para "cancelled"

3. **`remove_job(job_id)`**
   - Remove um job do banco de dados

4. **`apply_output_path_mapping(path)`**
   - Aplica mapeamento de caminhos para Docker

---

## Plano de Correção

### Passo 1: Adicionar funções faltantes ao `transcoder.py`

### Passo 2: Verificar a chamada do `effeff_transcode`
O código atual usa parâmetros incorretos:
```python
# ERRADO:
effeff_transcode(
    input_path=media_item.path,
    output_path=output_path,
    preset_config=preset,
    ...
)

# CORRETO (baseado na assinatura da função):
effeff_transcode(
    input_file=media_item.path,
    output_file=output_path,
    presets_data={preset_name: preset},
    preset_name=preset_name,
    ...
)
```

### Passo 3: Testar o build Docker

---

## Comandos para Build e Teste Local

```powershell
# 1. Navegar para o diretório do projeto
cd c:\Users\sk4rf\OneDrive\Documentos\Softwares\Repositorios\squishy-converter

# 2. Build da imagem Docker
docker-compose -f docker-compose.dev.yml build

# 3. Subir o container
docker-compose -f docker-compose.dev.yml up -d

# 4. Ver logs em tempo real
docker-compose -f docker-compose.dev.yml logs -f

# 5. Parar o container
docker-compose -f docker-compose.dev.yml down
```

---

## Próxima Ação Recomendada

> [!IMPORTANT]
> Antes de fazer o build, preciso corrigir o `transcoder.py` adicionando as funções `start_transcode`, `cancel_job`, `remove_job` e `apply_output_path_mapping`.

Deseja que eu faça essas correções agora?
