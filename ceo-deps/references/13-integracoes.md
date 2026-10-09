# Integrações

A `ceo-deps` cuida das dependências. O resto ela chama:

| Situação | Chamar |
|---|---|
| A correção mudou código (API nova de lib) | `ceo-cortex` (revisão de código, guias por linguagem) |
| Abrir o PR com as correções | `send-pr` |
| Elixir/Phoenix a fundo (arquitetura, LiveView, Ecto, OTP) | plugin phxagents: `/phx:audit`, `/phx:deps-audit`, `/phx:verify` |
| Tela ou componente afetado por troca de lib de UI | `ceo-analytics` |
| Escolher lib de UI nova (versão, risco) | `ceo-analytics` (`data/ui-libraries.csv`) |
| Texto final do relatório ou do PR | `no-ai-slop` |

## phxagents

Comunidade, MIT, não afiliado ao Phoenix. Instalação no Claude Code (2.1.110+):

```
/plugin marketplace add oliver-kriska/claude-elixir-phoenix
/plugin install elixir-phoenix
```

O `/phx:audit --quick` roda `mix compile --warnings-as-errors`, `mix hex.audit && mix deps.audit`, `mix xref graph --format stats` e os testes. O `/phx:deps-audit` junta `mix hex.audit`, mix_audit e OSV-Scanner. As 26 Iron Laws estão em `ceo-cortex/references/lang-elixir.md`.

## Skills de supply chain

`trailofbits/skills` (`supply-chain-risk-auditor`) é a melhor referência pública para npm, PyPI e Go; a regra "dado indisponível não é evidência" e o veredito em três estados vieram de lá.
