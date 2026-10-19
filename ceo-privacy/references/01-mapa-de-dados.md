# Mapa de dados pessoais

O mapa responde, por tipo de dado: o que coleta, para quê, onde guarda, quem acessa, para quem vai e por quanto tempo. Tudo o resto (rótulo da loja, política, exclusão, incidente) sai daqui.

## 1. Varredura automática (só leitura)

```bash
python3 scripts/pii_scan.py <app> [<servidor> ...] [--json] [--max 15] [--include-tests]
```

O que o script vê:

| Seção | Lê |
|---|---|
| Mapa | Ecto (`schema` e migrations), Prisma, TypeORM, Drizzle, SQL (`CREATE TABLE`, `ALTER TABLE ... ADD`), interfaces e tipos TS, objetos zod |
| Achados | log e analytics com dado pessoal ou credencial, armazenamento sem criptografia no aparelho, dado pessoal literal no código, exclusão de conta e link da política ausentes |
| SDKs | `package.json` e `mix.exs` contra `data/sdks.csv` |
| Permissões | `app.json`, `app.config.*`, `AndroidManifest.xml`, `Info.plist` |

Cada achado tem id de `data/checks.csv`, com severidade e fonte. Categorias e o que é sensível: `data/categorias.csv`.

Limites (diga "não verificado" quando importarem):
- Classifica pelo nome do campo. `value jsonb` com perfil inteiro dentro não aparece; abra o tipo que é gravado ali.
- Não vê dado guardado pelo provedor de login (ex.: tabela de usuários gerenciada pelo Supabase Auth ou Firebase Auth), buckets de arquivos, backups, planilhas, CRM nem painel de suporte. Pergunte ou leia a config.
- `app.config.ts` é código: permissões montadas em tempo de build podem faltar. Use o JSON de `npx expo config --json` se precisar.
- Pastas de teste ficam fora, a não ser com `--include-tests`.
- Exit code 1 quando há P1; 2 quando o caminho é inválido ou nada foi varrido.

## 2. Completar à mão

Para cada categoria achada, preencha `assets/inventario-dados-template.md`:
- **Finalidade:** para que o app usa (uma frase de produto, não jurídica).
- **Base legal provável:** `02-base-legal-e-consentimento.md`. Marque "confirmar com advogado".
- **Onde fica:** tabela, aparelho (SecureStore, AsyncStorage), SDK.
- **Quem acessa:** time interno (papel), fornecedor (operador), outro usuário do app.
- **Retenção:** `07-retencao-e-exclusao.md`. Sem prazo definido é achado P2.
- **Sai do país?** Servidor e SDKs fora do Brasil são transferência internacional (`05-terceiros-e-sdks.md`).

## 3. Conferir minimização

Para cada campo: o app precisa disso para funcionar? Campo coletado "para um dia usar" contraria o princípio da necessidade (LGPD art. 6, III) [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm]. Proponha tirar, não guardar ou guardar menos (ano em vez de data de nascimento completa, bairro em vez de coordenada).

## Saída

Inventário em `.ceo/privacy/inventario.md` (fora do git), sem nenhum valor real. No relatório, só o resumo por tipo.
