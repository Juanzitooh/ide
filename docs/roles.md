# Roles e permissoes por missao

Este documento descreve as permissoes atuais por missao. Nao existe escopo
global nesta fase.

## Roles

- admin: todas as permissoes da missao.
- lider: promove apoiadores para voluntarios e atua na operacao diaria.
- editor: publica conteudos institucionais e atualizacoes.
- financeiro: registra transparencia e dados financeiros.
- voluntario: acessa ferramentas internas e fluxo operacional.
- apoiador: recebe atualizacoes e pode se candidatar.

## Permissoes (resumo)

- content.write: editar paginas, imagens e redes.
- content.publish: publicar conteudos e atualizacoes.
- finance.read: ver dados financeiros.
- finance.write: registrar dados financeiros.
- donors.read: ver informacoes de apoiadores.
- operations.use: usar ferramentas internas.
- supporter.promote: promover apoiador para voluntario.
- supporter.apply: candidatar-se a voluntariado.
- updates.subscribe: receber atualizacoes.

## Estrutura base no JSON

```json
{
  "users": [
    {
      "name": "Ana Admin",
      "email": "ana.admin@missao-teste.org",
      "role": "admin",
      "status": "active"
    }
  ]
}
```

## Principios

- Menos roles e mais clareza.
- Facilitar burocracia sem abrir mao de seguranca.
- Nada de custo extra no MVP.

## Plano de implementacao (interrelacionado)

Objetivo: reduzir o tempo de gerenciamento de pessoas e projetos com um fluxo
unico de autenticacao, contato e visibilidade, mantendo as roles atuais.

Referencia cruzada:
- `docs/autenticacao_google.md`: login e seguranca (OAuth + sessao).
- `docs/infra_email_autenticacao.md`: email institucional, contato rapido, chat e
  links de reuniao.
- `docs/briefing_gerencia_projetos.md`: fluxo de projetos por missao.

### 1. Identidade e acesso (base para roles)

- Implementar login com Google.
- Criar/atualizar usuario local pelo email.
- Mapear role por missao no primeiro login.
- Permitir Admin promover/rebaixar role.

Resultado: elimina cadastro manual e senha local, reduzindo suporte.

### 2. Contato rapido e comunicacao

- Perfil de usuario com email institucional (pessoa+role+dominio).
- Links de contato (redes sociais opcionais).
- Botao "Adicionar contato" para chat 1:1.
- Campo de link de reuniao nas missoes/projetos.

Resultado: reduz tempo gasto em troca de informacoes e combinacoes informais.

### 3. Fluxo de projetos integrado as roles

- Admin cria missao e autoriza projetos (briefing PMBOK).
- Lider planeja e executa com voluntarios.
- Editor publica atualizacoes e status.
- Financeiro registra custos e transparencia.
- Voluntario executa tarefas e reporta progresso.

Resultado: clareza de responsabilidades e menos retrabalho.

### 4. Progresso e status automatico

- Status de missao/projeto deriva do progresso das tarefas.
- Relatorio simples de desempenho para o Admin.
- Licoes aprendidas ao encerrar projeto.

Resultado: visao rapida do estado sem reunioes longas.
