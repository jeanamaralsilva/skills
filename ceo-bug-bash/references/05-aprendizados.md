# 05. Aprendizados: modelo

Os aprendizados são do projeto, não da skill: a skill instalada é compartilhada entre projetos e é sobrescrita no update. Por isso o log fica no repo do app, em `.ceo/aprendizados.md`.

**Primeira rodada num repo:** se `.ceo/aprendizados.md` não existe, copie este modelo para lá (só o bloco abaixo) e preencha "Onde este app costuma quebrar" com os padrões de `06-aprendizados-exemplo.md` que se aplicam à stack. Eles são semente: viram linha do projeto só depois de testados nele.

Decida com o dono se `.ceo/` entra no git (o time aprende junto) ou fica em `.git/info/exclude` (só local).

Formato de cada linha: `- [AAAA-MM-DD] padrão → onde procurar da próxima vez (evidência)`.
- **padrão:** o defeito em termos que se repetem em outra tela, não o bug de um dia.
- **onde procurar:** a busca ou o passo que acha o próximo (arquivo, grep, tela, ação).
- **evidência:** print, PR ou sessão de onde veio. Sem evidência, não entra.

Se um tipo de defeito aparece 2 vezes, ele vira regra do projeto (um grep ou lint em `.ceo/` ou no CI do app, não no `ugly_scan.py` instalado, que é sobrescrito no update; regra que serve a qualquer app vira sugestão ao usuário, sem dado do projeto; nunca PR público por conta própria) ou charter novo nas notas do projeto.

---

```markdown
# Aprendizados de bug deste app

Formato: `- [AAAA-MM-DD] padrão → onde procurar da próxima vez (evidência)`.

## Onde este app costuma quebrar

- [2026-10-17] Texto legal (política/termos) descrevendo função desligada por flag (mapa, aula avulsa, localização) e fornecedor com finalidade errada (PostHog como "erros") → a cada flag ou SDK novo, grep da política por cada função e fornecedor; teste de controller que falha se a página citar função desligada.
- [2026-10-17] PR antigo que parece ter diff mas já está na main: `git diff main...branch` usa a base velha → antes de mergear PR parado, merge num worktree a partir de origin/main e `git diff origin/main` (vazio = fechar).

- [2026-10-17] Decisão tomada antes do lock (renovação x primeiro contrato lida fora da transação travada) → em todo job que gera N itens, aceite dois registros do mesmo dono ao mesmo tempo (xargs -P) e compare com a execução em sequência.
- [2026-10-17] Unicidade só com exists? (aluno duplicado em POST simultâneo) → duplo POST paralelo em todo cadastro com chave natural; índice parcial é perigoso quando há reativação automática (prefira lock por chave).
- [2026-10-17] Campo limpo enviado como undefined some do JSON e o servidor não apaga (cast só altera o que chega) → em toda edição, limpe cada campo opcional, salve, reabra e confira por GET.
- [2026-10-17] Mensagens de changeset em inglês por falta de Gettext pt_BR; o app às vezes casa texto inglês ("has already been taken"): grep no app antes de traduzir.
- [2026-10-17] Ambiente: teste de carga pesado derrubou o Postgres do Docker local (OrbStack) e o disco enche com log do servidor, prints e simulador → servidor de QA sem log em arquivo, no máximo 50 requisições paralelas, 2 agentes por vez, simulador só no fim.

## Falsos positivos que já enganaram

## Atalhos de ambiente que funcionam

## Charters que renderam mais
```
