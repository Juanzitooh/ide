# AGENTS.GLOBAL

Este arquivo orienta o Codex sobre como trabalhar neste repo.

## Objetivo do projeto

- Manter um MVP simples para apresentar missoes e suas informacoes publicas.
- Evitar complexidade desnecessaria e dependencias novas sem justificativa.
- Garantir que o app rode com `python app.py` ou `./deploy.sh`.

## Regras praticas

- Preserve a estrutura atual de pastas e o estilo existente.
- Prefira mudancas pequenas e localizadas.
- Use somente ASCII ao editar ou criar arquivos, a menos que o arquivo ja use Unicode.
- Para mudancas em HTML/CSS, seguir `docs/responsividade.md`.
- Registre mudancas de features ou ajustes importantes no `CHANGELOG.md`.
- Nao commitar `.env`; use `.env.example` como base.
- Dados de missoes ficam em `instance/missions.json`.
- Toda mudanca deve reduzir burocracia mantendo seguranca.

## Padroes tecnicos

- Flask com factory `create_app`.
- Rotas publicas em `app/routes`.
- Utilitarios de missao em `app/core`.
- Templates em `app/templates`.

## Python

- Siga o guia de clean code em `/home/jp/.codex/guides/python_guide.md`.
- Evite funcoes grandes; prefira guard clauses quando fizer sentido.
