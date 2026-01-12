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
