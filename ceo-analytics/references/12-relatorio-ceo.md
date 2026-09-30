# Relatório CEO

Curto, de dono para CEO. O modelo está em `assets/report-template.md`.

## Estrutura

1. **Veredito:** 2 frases. O estado do app e a maior alavanca. Pode trazer a nota da rubrica numa linha.
2. **Mapa:** uma tabela curta com tela, para que existe e estados faltando. Para app grande, só as telas do fluxo principal. O mapa completo vai num anexo, se o Jean pedir.
3. **Achados:** no máximo 7, ordenados de P0 a P3. Formato fixo, uma linha cada:
   `- **P1** <problema> → <mudança concreta> <evidência>`
   A evidência é `arquivo.tsx:linha`, `[tela: Nome]` ou `[print: arquivo.png]`.
4. **Propostas:** link ou print de cada alternativa, qual é a recomendada e por quê, em uma frase.
5. **Pendente do Jean:** só o que só ele decide (público, prioridade de negócio, acesso). Se não houver, a seção não aparece.

## Limites

- **600 palavras** por padrão. Se o Jean pedir relatório completo, suba o limite com `--max-words` e mantenha o resto das regras.
- **Nenhuma seção de "metodologia"** nem de "próximos passos genéricos".
- Nenhum travessão e nenhum jargão (`lint_report.py`).

## Onde entregar

- Resposta no chat quando for curto.
- Arquivo `.md` no repo (ex.: `docs/ux/<data>-analise.md`) quando o Jean for compartilhar com o time. Só crie no repo se ele pedir. Numa análise read-only (caso WAYUP), nada é escrito no repo.

## Checagem final

```bash
python <skill>/scripts/lint_report.py relatorio.md
```

Depois, o subagente `agents/report-reviewer.md` com modelo barato. Aplique o que ele apontar que viole as regras. Sugestões de reescrita que mudam o sentido técnico são descartadas.
