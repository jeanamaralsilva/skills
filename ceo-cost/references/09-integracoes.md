# Integrações

A `ceo-cost` cuida da conta. O resto ela chama, se a skill estiver instalada; sem ela, diga o que ficou de fora.

| Situação | Chamar |
|---|---|
| Trocar biblioteca, SDK ou serviço pago por outro (ex.: storage, analytics, e-mail) | `ceo-deps` (passe o serviço, a economia em faixa e o risco) |
| Builds no EAS, perfis do `eas.json`, update pelo ar em vez de build, canal de update | `ceo-ship` |
| Levar custo do mês e plano de corte ao update do dono, sócio ou investidor | `ceo-brief` (passe a primeira linha do relatório e as decisões) |
| Conta subindo agora: chave vazada, loop chamando API, ataque, gasto sem teto disparando | `ceo-incident` para conter; volte aqui para medir o custo e o corte |
| Revisar a mudança de código que corta custo (cache, gatilho de CI, imagem menor) | `ceo-code-review` |
| Provar que o app segue funcionando depois do corte | `ceo-mobile-qa` |
| Mudar região ou fornecedor que guarda dado pessoal | `ceo-privacy` |
