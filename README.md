# Ide e Pregai

Ide e Pregai e uma plataforma aberta para apoiar missoes cristas com transparencia,
organizacao e comunicacao simples. O foco e reduzir o peso burocratico, tornar o
trabalho visivel e facilitar o acompanhamento por quem deseja orar, apoiar ou
entender o que esta acontecendo no campo.

> "Ide por todo o mundo e pregai o evangelho a toda criatura." (Marcos 16:15)

## Proposta (versao melhorada)

- Dar visibilidade a missoes reais sem intermediar recursos financeiros.
- Manter dados claros, publicos e atualizaveis pelos proprios missionarios.
- Facilitar o acesso a informacoes basicas: quem, onde, como servir e como orar.
- Ser simples de operar, leve de hospedar e totalmente open source.

## Principios do MVP

- Um app, multiplas missoes.
- Sem banco pesado no inicio (JSON simples).
- Paginas publicas com identidade e dignidade.
- Preparado para subdominios, sem obrigar isso agora.

## Arquitetura do MVP

- Flask com factory `create_app`.
- Dados em `instance/missions.json`.
- Resolucao por slug (`/m/<slug>`) e por subdominio quando existir.
- Paginas institucionais por missao (`/m/<slug>/sobre`, `/m/<slug>/projetos`, `/m/<slug>/ajuda`, `/m/<slug>/contato`).
- Painel simples autenticado com Google (`/login`, `/m/<slug>/painel`).
- Detalhes de projeto (`/m/<slug>/projetos/<project_id>`) e chat basico (`/m/<slug>/chat`).
- Feedback simples para bugs e sugestoes (`/feedback`).
- Financeiro basico por missao (`/m/<slug>/financeiro`).
- Lancamentos com vinculo opcional a projetos com orcamento.
- Caixa central com orcamentos distribuiveis por projeto.
- Panorama financeiro diario/semanal/mensal/anual com exportacao CSV.
- Dashboard da missao mostra projetos e dados financeiros com filtro de encerrados.
- Templates basicos com layout pronto para evolucao.

## Estrutura do projeto

```
app/
  app.py
  __init__.py
  config.py
  core/
    guards.py
    auth.py
    progress.py
    tenant.py
  routes/
    auth.py
    health.py
    public.py
  templates/
    base.html
    index.html
    mission.html
    mission_about.html
    mission_projects.html
    mission_project_detail.html
    mission_dashboard.html
    mission_chat.html
    login.html
    mission_help.html
    mission_contact.html
    mission_not_found.html
instance/
  missions.json
app.py
requirements.txt
.env.example
```

## Como rodar localmente

```bash
./deploy.sh
```

Acesse:

```
http://localhost:5000
```

Exemplo de slug:

```
http://localhost:5000/m/ide
```

Exemplos de paginas institucionais:

```
http://localhost:5000/m/ide/sobre
http://localhost:5000/m/ide/projetos
http://localhost:5000/m/ide/ajuda
http://localhost:5000/m/ide/contato
```

## Variaveis de ambiente (login Google)

```bash
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback
SECRET_KEY=...
```

## Usar MySQL (MariaDB) + Redis

1. Crie o banco e importe o schema:

```bash
mysql -u root -p -e "CREATE DATABASE ide;"
mysql -u root -p ide < schema.sql
```

2. Defina as variaveis:

```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=seu_usuario
MYSQL_PASSWORD=sua_senha
MYSQL_DB=ide
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_TTL_MISSION=600
REDIS_TTL_LIST=120
```

Com isso, o app passa a ler/gravar no MySQL e usar Redis como cache.

## Produção com Gunicorn

```bash
USE_GUNICORN=1 ./deploy.sh
```

Variaveis opcionais:

- `GUNICORN_WORKERS` (padrao: 2)
- `GUNICORN_THREADS` (padrao: 4)
- `GUNICORN_TIMEOUT` (padrao: 30)

## Rodar testes rapidos

```bash
python app.py --test
```

O relatório é salvo em `instance/test_report.json`.

## Proximos passos sugeridos

- Cadastro simples para missao (admin local).
- Painel interno para atualizar a pagina publica.
- Exportacao de relatarios por missao.
- Preparar deploy em VPS simples.
