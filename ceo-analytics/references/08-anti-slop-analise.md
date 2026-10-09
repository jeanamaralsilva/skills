# Anti-slop na análise: relatório curto, sem dado que não precisa

O CEO quer isso: relatório reduzido, sem os vícios de IA de encher análise com dado que não muda nada. Esta é a parte da skill que mais separa um designer sênior de um gerador de texto.

## O teste do corte

Para cada linha, pergunte: **se eu tirar isto, o CEO decide diferente?** Se a resposta for não, corte. Isso elimina:

- Descrever o que ele já vê ("a tela tem um header com o logo e um botão azul").
- Repetir o mesmo achado com outras palavras em seções diferentes.
- Heurística que passou sem problema. Nota 4 não vira parágrafo.
- Contexto genérico sobre UX ("a usabilidade é fundamental para o sucesso de um app").
- Resumo no fim que repete o começo.

## Os oito vícios (AA01 a AA08 em `data/anti-patterns.csv`)

| ID | Vício | Correção |
|---|---|---|
| AA01 | "Melhorar a acessibilidade" | Tela + elemento + problema + mudança: "Botão Salvar em `TreinoScreen.tsx:88` tem 32pt; subir para 44pt" |
| AA02 | Achado sem evidência | Arquivo:linha, `[tela: ...]` ou `[print: ...]`. Sem isso, o achado sai |
| AA03 | Heurística alucinada | Só reportar o que foi visto no código ou no app. Na dúvida, escrever "não verificado" |
| AA04 | Número inventado | `[medido]` com o script ou a ferramenta, `[fonte: url]`, ou `[estimado]` com a base do cálculo |
| AA05 | Lista longa sem prioridade | No máximo 7 achados no corpo, ordenados P0 a P3. O resto não entra |
| AA06 | Dado óbvio | Teste do corte |
| AA07 | Análise só por texto | Conclusão de usabilidade exige render real (app rodando ou export do design) |
| AA08 | Heurística de eficiência chutada | Percorrer a tarefa e contar os toques (`04`) |

## O que nunca inventar

- **Métricas de produto:** NPS, taxa de conversão, retenção, tempo médio de sessão. Sem acesso ao analytics, não existem.
- **Personas.** Sem pesquisa, "a Maria, 32 anos, que treina às 6h" é ficção.
- **"Estudos mostram"** sem link.
- **Contraste** sem `contrast.py`.
- **"Usuários preferem"** sem review, estudo ou prêmio.

## O que o lint pega sozinho

```bash
python <skill>/scripts/lint_report.py - <<'EOF'
<texto da resposta>
EOF
```

| Regra | Pega |
|---|---|
| `em-dash` | travessão |
| `jargon` | robusto, abrangente, seamless, leverage, elevar... |
| `vague-fix` | "melhorar a usabilidade" e similares |
| `unsourced-number` | % ou `x:1` sem etiqueta na linha |
| `no-evidence` | linha de achado `- **P1** ...` sem arquivo, tela ou print |
| `too-long` | acima do limite de palavras |

O lint não pega dado óbvio, repetição nem severidade inflada. Isso é julgamento seu, e o `agents/report-reviewer.md` confere uma segunda vez.

## Exemplo

**Ruim:**
"Analisando a tela de treinos, podemos observar que ela apresenta uma estrutura robusta com cards bem definidos. No entanto, há oportunidades de melhorar a experiência do usuário, tornando-a mais intuitiva. Estudos mostram que 70% dos usuários abandonam apps com carregamento lento."

**Bom:**
"- **P0** Carga da série não persiste ao sair do app `src/features/workout/useSets.ts:41` (estado só em memória)."
