# Traduzir sinais para negócio

Tabela completa com fonte: `data/sinais.csv`. Aqui, o jeito de usar.

## As três perguntas

1. **Chegou ao cliente?** Deploy em produção com estado `success` (S02), versão na loja ou atualização pelo ar (S04). Mergeado é "pronto" (S01). Se não dá para saber, "pronto, entrega não verificada".
2. **O que está em risco?** Em ordem de peso: incidente ou reversão (S07, S18), CI falhando na base (S10), mudança que quebra compatibilidade (S15), bug aberto antigo (S12), frente parada (S11), dado velho (S16).
3. **Quanto falta?** `references/03-quanto-falta.md`.

## Agrupar por resultado

- Junte commits e PRs pelo que o cliente sente: "cadastro mais rápido", "erro de pagamento corrigido". Use o escopo do commit (`feat(pagamento): ...`) e a área de pasta (`git.areas`) como pista, não como texto final.
- Correção que o cliente nunca viu (teste, refatoração, CI) vira uma linha: "manutenção interna: N mudanças sem efeito visível". Não esconda, não destaque.
- Mudança de segurança: diga que foi feita e o efeito ("senhas agora expiram"), sem detalhar a falha que existia.

## Métricas de entrega (DORA)

As cinco métricas do DORA hoje: frequência de deploy, tempo da mudança até produção, taxa de falha de mudança, tempo de recuperação de deploy com falha e taxa de retrabalho [fonte: https://dora.dev/guides/dora-metrics/]. Use só as que o dado sustenta:

| Métrica | Dá para tirar do coletor? | Como dizer |
|---|---|---|
| Frequência de deploy | sim, se o provedor grava deployment no GitHub | "entregamos 6 vezes nesta semana" |
| Tempo até produção | não | só se o dono ou o time medir |
| Taxa de falha | parcial: reversões e correções logo após deploy | "1 de 6 entregas precisou ser desfeita" |
| Recuperação | não sem dado de incidente | "o problema durou 2 horas" só com relato |
| Retrabalho | parcial | "parte da semana foi apagar incêndio" |

Regras do próprio DORA: métrica não vira meta (o time passa a jogar com o número) e não serve para comparar times diferentes [fonte: https://dora.dev/guides/dora-metrics/]. No brief, compare com o próprio histórico.

## Disponibilidade

Se o time tem meta de disponibilidade (SLO), o "orçamento de erro" é 100% menos a meta. Quando ele acaba, a regra do SRE é congelar mudanças até recuperar [fonte: https://sre.google/workbook/implementing-slos/]. Para o dono: "vamos pausar novidades para estabilizar". Sem SLO definido, não invente um.
