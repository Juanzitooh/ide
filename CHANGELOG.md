# Changelog

Todas as mudancas relevantes devem ser registradas aqui.

## [Unreleased]

- Adicionado login com Google (OAuth) e base de sessao para acesso ao painel.
- Incluidos painel da missao, detalhes de projetos, chat simples e progresso por tarefas.
- Adicionadas estruturas de progresso, chat e reunioes em `instance/missions.json`.
- Implementada criacao de reunioes via Google Meet API com OAuth dedicado.
- Adicionada pagina de feedback com registro em `instance/feedback.json`.
- Ajustadas telas de erro de autenticacao e links de retorno ao painel.
- Adicionada area financeira basica com lancamentos e resumo por missao.
- Adicionado orcamento por projeto e lancamentos vinculados por lider/voluntario.
- Adicionado caixa central com orcamento distribuido por projeto.
- Adicionado panorama financeiro por periodo e exportacao CSV.
- Dashboard mostra projetos, status e resumo financeiro com filtro de encerrados.
- Dashboard destaca projetos encerrados recentemente e registra closed_at automaticamente.
- Adicionado suporte opcional a MySQL com schema e dados de exemplo.
- Substituido JSON por MySQL com cache Redis (cache-aside).
- Otimizacoes: pool de conexoes, Redis singleton, indices e Gunicorn opcional.
- Adicionado `gunicorn.conf.py` com auto-configuracao por variaveis.
- Adicionado modo `--test` com verificacoes e teste de carga simples.
- Adicionadas paginas institucionais por missao (sobre, projetos, ajuda, contato) e pagina de nao encontrada.
- Expandido `instance/missions.json` com dados estruturados (sobre, projetos, ajuda, contato).
- Criada base de docs de demandas e backlog de features com foco em baixo custo.
- Documentadas roles por missao e adicionados usuarios de teste em `instance/missions.json`.
- Adicionadas diretrizes de responsividade para HTML/CSS.
- Adicionado indice de documentacao em `docs/README.md`.
