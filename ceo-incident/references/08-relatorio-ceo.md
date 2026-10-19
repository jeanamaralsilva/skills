# Relatório CEO

Curto, de dono técnico para dono do negócio, durante e depois.

## Durante (cada update)

Modelo: `assets/update-dono-template.md`. Até 120 palavras.

1. **Linha 1:** severidade, estado, hora. "SEV2, monitorando, 14:40."
2. **Impacto:** quem, quantos, o que não conseguem fazer, desde quando. Número com origem.
3. **Agora:** ação em curso ou mitigação feita e a evidência.
4. **Causa:** provável, confirmada ou "ainda não sabemos".
5. **Decisão sua:** o que só o dono decide (avisar clientes, pausar lançamento, aceitar risco) ou "nenhuma".
6. **Próximo update:** hora.
7. **Não verificado:** o que não deu para ver.

## Ação em produção pendente

Bloco separado, completo mesmo que fique longo:
```
Proposta: <ação>
Comando: <comando exato>
Muda: <o que>
Não desfaz: <migração, quem já baixou, variáveis>
Confirma assim: <sinal>
Responda "sim, pode rodar" para eu executar.
```

## Depois

Postmortem (`assets/postmortem-template.md`) e, se pedido, texto ao cliente. Até 400 palavras no postmortem; o resumo de 3 frases basta sozinho.

## Nunca

- Metodologia, lista de comandos lidos, log colado.
- Nome de pessoa para culpa.
- Segredo, dado pessoal, stack trace.
- "Resolvido" sem o sinal do cliente de volta ao normal.
- "Ok" para o que não foi verificado.
