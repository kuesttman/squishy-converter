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
git clone https://github.com/cleverdevil/squishy.git
cd squishy
```
2. Modifique o docker-compose.yml:
   - Descomente e edite as montagens de volume do caminho de mídia nos serviços Squishy e Jellyfin/Plex
   - Descomente as configurações apropriadas de GPU/aceleração de hardware, se necessário
   - Escolha Jellyfin ou Plex (comente o que você não usa)

3. Inicie os contêineres:
```bash
docker compose up --build
```

4. Acesse o Squishy:

Abra seu navegador e navegue até `http://seu-host:5101`. O Squishy irá guiá-lo pelo resto do processo de configuração!

### Usando a Imagem Docker Pré-construída

Uma imagem Docker pré-construída está disponível no GitHub Container Registry. Você pode baixá-la usando:

```bash
docker pull ghcr.io/OWNER/REPO:latest
```

Substitua `OWNER` pelo seu nome de usuário do GitHub e `REPO` pelo nome do repositório.

**Nota:** Se o seu repositório for privado, você pode precisar autenticar no GitHub Container Registry ou alterar as configurações de visibilidade do pacote no seu repositório GitHub na guia "Packages".

### Aceleração de Hardware

O Squishy atualmente suporta VA-API para transcodificação acelerada por hardware. O suporte para outros métodos de aceleração pode ser adicionado se houver uma forte demanda dos usuários.

Por baixo do capô, o Squishy usa um projeto embutido chamado `effeffmpeg`, que lida com toda a transcodificação e interface com o ffmpeg. Mais detalhes estão disponíveis no [effeffmpeg README.md](https://github.com/cleverdevil/squishy/blob/main/squishy/effeffmpeg/README.md) na árvore de fontes.
