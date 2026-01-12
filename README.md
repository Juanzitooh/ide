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
- Templates basicos com layout pronto para evolucao.

## Estrutura do projeto

```
app/
  app.py
  __init__.py
  config.py
  core/
    guards.py
    tenant.py
  routes/
    health.py
    public.py
  templates/
    base.html
    index.html
    mission.html
    mission_about.html
    mission_projects.html
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

## Proximos passos sugeridos

- Cadastro simples para missao (admin local).
- Painel interno para atualizar a pagina publica.
- Exportacao de relatarios por missao.
- Preparar deploy em VPS simples.
