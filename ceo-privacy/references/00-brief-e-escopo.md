# Brief e escopo

Defina em silêncio, pelo repo e pelo `.ceo/config.md` (seção ceo-privacy). Pergunte só o que muda a ação e não dá para descobrir.

## Modo

| Pedido | Modo | Começa por |
|---|---|---|
| "estou ok com a LGPD?", auditoria, "o que eu coleto?" | **auditoria** | `01-mapa-de-dados.md` |
| App Privacy, Data safety, rótulo, privacy manifest, ATT | **lojas** | `04-lojas-e-rotulos.md` |
| "excluir conta", pedido de cliente para ver, corrigir ou apagar dados | **titular** | `03-direitos-do-titular.md` |
| vazamento, dado exposto, "o CPF apareceu no log" | **incidente** | `08-incidente.md` |
| política de privacidade, termos | **política** | `10-politica-e-termos.md` |
| SDK novo, "posso colocar o analytics X?" | **terceiros** | `05-terceiros-e-sdks.md` |
| app para criança ou adolescente | **menores** | `09-criancas-e-adolescentes.md` |

Vários ao mesmo tempo: comece pelo incidente, se houver; depois mapa de dados, que alimenta todos os outros.

## Perguntas que mudam a ação

1. **Onde estão os usuários?** Só Brasil: LGPD. Oferece para pessoas na UE: GDPR também. EUA com menores de 13: COPPA.
2. **Menores de 18 usam ou podem usar?** Muda base legal, rótulo da loja e regras de produto.
3. **É agente de pequeno porte?** Muda prazos e obrigações na ANPD (`data/requisitos.csv`). Quem decide se enquadra é o advogado ou o contador; a skill só aponta o critério.
4. **Repos:** app, servidor, painel web. Read-only? Então só relatório.
5. **O app tem conta?** Sem conta, exclusão de conta não se aplica, mas o resto sim.

## Fora do escopo

- Parecer jurídico, escolha final de base legal, texto final da política: advogado.
- Segurança geral do servidor (autenticação, autorização, injeção): só quando expõe dado pessoal; o resto é `ceo-code-review`.
- Subir versão: `ceo-ship`. Conter incidente em produção: `ceo-incident`.
