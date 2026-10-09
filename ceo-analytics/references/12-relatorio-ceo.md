# Relatório CEO

Curto, de dono para CEO. Se der para dizer em 5 linhas, são 5 linhas. O modelo está em `assets/report-template.md`.

## Estrutura

1. **Veredito:** 2 frases. O estado do app e a maior alavanca. Pode trazer a nota da rubrica numa linha.
2. **Mapa:** uma tabela curta com tela, para que existe e estados faltando. Para app grande, só as telas do fluxo principal. O mapa completo vai num anexo, se o CEO pedir.
3. **Achados:** no máximo 7, ordenados de P0 a P3. Formato fixo, uma linha cada:
   `- **P1** <problema> → <mudança concreta> <evidência>`
   A evidência é `arquivo.tsx:linha`, `[tela: Nome]` ou `[print: arquivo.png]`.
4. **Propostas:** link ou print de cada alternativa, qual é a recomendada e por quê, em uma frase.
5. **Pendente do CEO:** só o que só ele decide (público, prioridade de negócio, acesso). Se não houver, a seção não aparece.

## Limites

- **Limite por modo** (passe com `--max-words`):
  - ajuste: 150
  - proposta: 350 (padrão do lint)
  - análise com mapa do app: 450

  Se o CEO pedir relatório completo, suba o limite e mantenha o resto das regras. Estourou? Corte antes de entregar, começando pelo que o CEO já sabe.
- **Nenhuma seção de "metodologia", "arquivos lidos", "ferramentas" ou "próximos passos genéricos".** A evidência mora dentro de cada achado.
- **O mapa entra só se o CEO pediu para entender o app.** Num pedido de proposta ou ajuste, ele fica fora.
- Nenhum travessão e nenhum jargão (`lint_report.py`).

## Onde entregar

- **Padrão: resposta no chat.** Não crie arquivo.
- Arquivo só se o CEO pedir (ex.: para compartilhar com o time). Numa análise read-only, nada é escrito no repo.
- Proposta visual vai para o Pencil (`14-fluxo-no-pencil.md`), e o chat traz só o resumo.

## Checagem final

```bash
python <skill>/scripts/lint_report.py - <<'EOF'
<texto da resposta>
EOF
```

Depois, o subagente `agents/report-reviewer.md` com modelo barato. Aplique o que ele apontar que viole as regras. Sugestões de reescrita que mudam o sentido técnico são descartadas.
