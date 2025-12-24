<center><img src="https://raw.githubusercontent.com/cleverdevil/squishy/main/squishy/static/img/splash.png"></center>

# Squishy: Transcodificação de Mídia Simplificada

Acumuladores digitais muitas vezes têm bibliotecas de mídia repletas de filmes e programas de TV em alta resolução. Quando você está assistindo na tela grande do seu home theater, você quer a melhor qualidade possível na forma de rips e remuxes de Blu-ray. Essa qualidade tem um custo - o tamanho do arquivo. Remuxes 4K HDR geralmente estão na faixa de 30-100 GB. Ao viajar, baixar mídia para o seu telefone com esses arquivos resulta em downloads longos e espaço de armazenamento limitado. Entra o Squishy, que torna a transcodificação e o download de sua mídia simples, automatizando o processo de transcodificação sob demanda, comprimindo seus grandes arquivos de mídia para tamanhos muito mais razoáveis para assistir filmes e programas de TV em dispositivos menores, como telefones e tablets.

## Funcionalidades

O Squishy possui um conjunto focado de funcionalidades projetadas para tornar o processo de seleção, transcodificação e download de sua mídia o mais simples possível:

* Interface web atraente para navegar em sua mídia e arquivos transcodificados, incluindo arte de pôster.
* Integração com servidores de mídia Jellyfin e Plex para adicionar rapidamente sua biblioteca de mídia ao Squishy.
* Predefinições de transcodificação flexíveis, dando a você a capacidade de otimizar para seu caso de uso. As predefinições definem uma resolução, codec e qualidade de destino. O Squishy vem com predefinições padrão, juntamente com bibliotecas de predefinições adicionais para diferentes compensações.
* Personalize e crie suas próprias predefinições para permitir que você ajuste suas preferências pessoais selecionando resoluções, taxas de bits e codecs personalizados.
* Suporte a aceleração de hardware com failover automático para codificação por software quando a aceleração de hardware falha.
* Links de download direto para sua mídia transcodificada que funcionam com qualquer navegador ou aplicativo reprodutor de mídia.

## Instalação

O Squishy pode ser executado manualmente a partir da fonte, mas o método de instalação recomendado é executar o Squishy como um contêiner Docker. O repositório inclui um arquivo `docker-compose.yml` para sua conveniência.

### Executando com Docker

1. Clone este repositório:
```bash
git clone https://github.com/kuesttman/squishy-converter.git
cd squishy-converter
```
2. Modifique o `docker-compose.yaml` (se necessário):
   - O arquivo já vem configurado para usar a imagem oficial do repositório: `ghcr.io/kuesttman/squishy-converter:main`.
   - Ajuste os volumes para apontar para suas pastas de mídia.
   - Ajuste as configurações de hardware se necessário.

3. Inicie os contêineres:
```bash
docker compose up -d
```

4. Acesse o Squishy:

Abra seu navegador e navegue até `http://seu-host:5101` (ou o domínio configurado no Traefik). O Squishy irá guiá-lo pelo resto do processo de configuração!

### Usando a Imagem Docker Pré-construída

A imagem Docker é construída e publicada automaticamente no GitHub Container Registry.

Para puxar a última versão manualmente:
```bash
docker pull ghcr.io/kuesttman/squishy-converter:main
```

**Nota:** Se o seu repositório for privado, você pode precisar autenticar no GitHub Container Registry.

### Aceleração de Hardware

O Squishy atualmente suporta VA-API para transcodificação acelerada por hardware. O suporte para outros métodos de aceleração pode ser adicionado se houver uma forte demanda dos usuários.

Por baixo do capô, o Squishy usa um projeto embutido chamado `effeffmpeg`, que lida com toda a transcodificação e interface com o ffmpeg. Mais detalhes estão disponíveis no [effeffmpeg README.md](https://github.com/cleverdevil/squishy/blob/main/squishy/effeffmpeg/README.md) na árvore de fontes.
