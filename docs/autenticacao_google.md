# Autenticacao com Google (OAuth 2.0 / OpenID Connect)

Este documento descreve como habilitar login com Google para o novo projeto,
com foco em seguranca de dados e controle de acesso por roles. O objetivo e
usar o Google apenas como provedor de identidade (autenticacao), mantendo a
autorizacao (roles por missao) dentro do sistema.

## Visao geral do fluxo

1. Usuario clica em "Entrar com Google".
2. Sistema redireciona para o Google com `state` e `nonce`.
3. Usuario autentica no Google e concede acesso basico.
4. Google retorna para o `redirect_uri` com `code`.
5. Backend troca o `code` por tokens e valida o `id_token`.
6. Sistema cria sessao local e associa o usuario a roles internas.

## Configuracao no Google Cloud (sem dominio)

1. Criar um projeto no Google Cloud Console.
2. Configurar a "OAuth consent screen" (External, se necessario).
3. Criar credenciais "OAuth client ID" do tipo "Web application".
4. Adicionar URLs locais:
   - Authorized JavaScript origins:
     - `http://localhost:5000`
   - Authorized redirect URIs:
     - `http://localhost:5000/auth/google/callback`
     - `http://localhost:5000/auth/google/meet/callback`

Obs: mesmo sem dominio, o Google permite `localhost` para desenvolvimento.
Quando houver dominio, adicionar as URLs de producao.

## Variaveis de ambiente sugeridas

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI` (ex: `http://localhost:5000/auth/google/callback`)
- `SESSION_SECRET_KEY`

## Escopos recomendados (minimo necessario)

- `openid`
- `email`
- `profile`

## Escopos adicionais (Meet)

Para criar espacos de reuniao via API do Google Meet:

- `https://www.googleapis.com/auth/meetings.space.created`

Evitar escopos sensiveis. O sistema precisa apenas identificar o usuario.

## Dados e seguranca

- Validar `state` para evitar CSRF.
- Validar `nonce` no `id_token` para evitar replay.
- Verificar assinatura e `aud` do `id_token` com a chave publica do Google.
- Usar cookies `HttpOnly` e `Secure` (em producao).
- Evitar armazenar `access_token` ou `refresh_token` no frontend.
- Guardar somente dados essenciais: `sub` (id), `email`, `name`.
- Definir expiracao de sessao e opcionalmente logout global.

## Roles e autorizacao (missao)

Autenticacao nao define permissoes. Apos login:

1. Buscar usuario interno pelo `email` ou `sub`.
2. Se existir, aplicar a role e permissoes da missao.
3. Se nao existir, criar como `apoiador` ou `pendente` (definir politica).
4. Admin pode promover roles conforme necessidade.

Sugestao: manter um registro simples com `email`, `role`, `status` por missao,
conforme `docs/roles.md`.

## Paginas/rotas sugeridas

- `/auth/google` (inicia o login)
- `/auth/google/callback` (processa o retorno)
- `/logout` (encerra a sessao local)
- `/login` (tela com botao do Google)

## Erros comuns

- Redirect URI nao cadastrado no Google Cloud.
- `state` nao confere (CSRF).
- `id_token` invalido ou expirado.
- Relogio do servidor com diferenca grande (validacao falha).

## Proximos passos

1. Definir politica de criacao de usuario (auto cadastro ou convite).
2. Definir como o Admin atribui roles por missao.
3. Implementar rotas e validacao de token no backend.
