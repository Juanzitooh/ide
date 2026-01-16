# Infra de E-mail e Autenticacao (ONG/Missao)

Este documento organiza a proposta de e-mail institucional e login com Google
para o projeto, priorizando custo zero, simplicidade e seguranca.

## 1. Faz sentido usar VPS + Mailcow?

Sim, desde que exista alguem tecnico para configurar e manter.

Quando faz sentido:
- Muitas pessoas na missao.
- Dominio proprio (`@missao.org.br`).
- Custo zero por usuario.
- Autonomia (sem depender de Google/Microsoft).

Quando nao e boa ideia:
- Ninguem tecnico para manter.
- Precisa de entregabilidade perfeita para campanhas massivas.

## 2. Arquitetura minima (Oracle Free Tier)

- 1 VM Ampere (ARM), 1-2 vCPU, 6 GB RAM, Ubuntu 22.04.
- Mailcow com Docker (Postfix, Dovecot, DKIM, antispam, interface web).
- DNS configurado uma vez: MX, SPF, DKIM, DMARC.

## 3. Integracao com o site (sem virar caos)

O site cria e gerencia pessoas e roles. O Mailcow fica por tras.

Fluxo sugerido:
1. Admin cria a Missao.
2. Admin cria pessoas e atribui roles.
3. Sistema cria email institucional automaticamente.
4. Usuario recebe acesso e senha temporaria.

Modelo recomendado: combinar pessoa + role + dominio.

Exemplos:
- `joao.silva.lider@missao-x.org.br`
- `maria.souza.financeiro@missao-x.org.br`
- `ana.pereira.editor@missao-x.org.br`
- `paulo.costa.voluntario@missao-x.org.br`
- `lucas.lima.apoiador@missao-x.org.br`

Esse modelo evita conta compartilhada e facilita auditoria e rastreio.

## 4. Autenticacao (login) x Email institucional

Sao duas coisas diferentes:

- Autenticacao: usar Google Login (OAuth 2.0).
- Email institucional: usar Mailcow para a funcao/role.

Nao e necessario o email institucional ser a mesma conta do login.

## 5. Envio confiavel (SMTP externo)

Para reduzir risco de spam e bloqueios:

- Recebimento: Mailcow na VPS.
- Envio: SMTP externo (SES, Brevo, Mailgun).

Isso mantem custo baixo e melhora entregabilidade.

## 7. Chat simples no site (opcional)

Se o email nao for usado, o site pode oferecer um chat simples entre usuarios,
com foco em recados basicos:

- Conversa 1:1 entre usuarios da mesma missao.
- Mensagens curtas e historico limitado.
- Usar apenas dentro do site, sem substituir email.

Esse chat serve como alternativa leve para comunicacao rapida.

## 8. Reunioes com link (Meet ou similar)

E possivel facilitar reunioes no site sem integrar video diretamente:

- Criar campo "Link da reuniao" no projeto/missao.
- Permitir adicionar link do Google Meet, Zoom ou Jitsi.
- Exibir o link na pagina do projeto e nos lembretes.
- Padrao simples: apenas salvar e copiar/abrir o link.

Isso reduz custo e complexidade, mantendo o fluxo simples.

Opcional: integrar com a API do Google Meet para criar o link automaticamente,
exigindo escopo adicional e configuracao no Google Cloud.

## 9. Contato rapido (perfil)

Para facilitar comunicacao entre pessoas da mesma missao:

- Perfil com links rapidos: redes sociais, email institucional e chat.
- Botao "Adicionar contato" para abrir chat 1:1.
- Opcao de ocultar redes pessoais; mostrar apenas o essencial.
- Permitir que o Admin defina quais campos sao obrigatorios.

## 6. Recomendacao final

Melhor opcao para ONG/Missao com custo zero:

- VPS Oracle + Mailcow para email institucional.
- Google Login para autenticacao do site.
- SMTP externo apenas para envio.
