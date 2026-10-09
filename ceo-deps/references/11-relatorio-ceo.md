# Relatório CEO

Curto, de dono para CEO. Modelo: `assets/report-template.md`.

## Estrutura

1. **Veredito:** 2 frases. Saudável ou não, e o maior risco.
2. **Por repo:** uma linha com stack e números que importam (ex.: "expo 57.0.4, 25 pacotes fora do SDK, 1 duplicata nativa, 2 lockfiles").
3. **Achados:** até 7, de P0 a P3, uma linha cada:
   `- **P1** <problema> → <correção> \`<arquivo:linha>\``
   Evidência: arquivo do repo (`package.json:12`, `mix.exs:92`), `[cmd: npx expo-doctor]` ou `[fonte: url]`.
4. **Feito** (modo manter): o que foi aplicado e até que degrau foi verificado.
5. **Pendente do Jean:** só decisões com trade-off real.

## Severidade

| Nível | Critério |
|---|---|
| P0 | CVE explorável em produção; pacote malicioso; licença deny; build nativo quebrado |
| P1 | duplicata nativa; regressão conhecida do SDK; dois lockfiles; lib central abandonada; chamada externa sem timeout no caminho principal |
| P2 | desatualizada fora do SDK/range; duplicação funcional; sem uso confirmada; dep git por tag; toolchain solta; sem bot |
| P3 | higiene (lock com sobra, override esquecido) |

## Limites

- Até 400 palavras por padrão; um repo só cabe em 250.
- Sem seção de "metodologia", "ferramentas usadas" ou lista de comandos rodados.
- Número sempre com origem: `[cmd: ...]`, `[medido]` ou `[fonte: ...]`.
- "Não verificado" quando a ferramenta não rodou. Nunca "ok" por omissão.

```bash
python scripts/lint_report.py - --max-words 400 <<'EOF'
<texto>
EOF
```
