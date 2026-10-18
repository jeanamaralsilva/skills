# Estratégia: onde o bug mora

Testar tudo com a mesma força é o jeito de não achar nada. O teste pesado vai onde o risco é maior; o resto recebe uma passada.

## Priorize por risco

Risco = probabilidade de quebrar × custo de quebrar. Para cada tela do mapa, pontue de 1 a 3:

| Probabilidade sobe quando | Custo sobe quando |
|---|---|
| escreve dado (mutation, push, upload) | é o fluxo que o produto vende (money tour) |
| tem tempo real (canal, presença, socket) | perde dado do usuário |
| depende de permissão, rede ou relógio | envolve dinheiro, nota, presença, prazo |
| foi mudada no último mês (`git log --since`) | dois papéis veem o mesmo dado |
| já teve bug (bad neighborhood) | não tem como desfazer |
| tem lista longa, mídia ou formulário grande | o cliente reclamou |

Telas com 5 ou 6: estresse completo (todos os caminhos da matriz, tours, rede ruim). Com 3 ou 4: caminho feliz, triste e duplo toque. Com 1 ou 2: só o feliz na varredura.

## As quatro fontes de bug num app com servidor

Estudo de 16 mil crashes em apps Android (Fan et al., ICSE 2018) e a experiência com apps React Native + Phoenix apontam para o mesmo lugar:

1. **Ciclo de vida:** background, process death, rotação, voltar com estado nulo. A categoria mais comum. Barato de provocar: `stopApp` e `launchApp` no Maestro, Home e volta, `xcrun simctl terminate`.
2. **Concorrência:** resposta chega depois de sair da tela, duas escritas ao mesmo tempo, dois clientes no mesmo registro. Provoca-se com duplo toque, Toxiproxy (latência) e o segundo ator.
3. **Recurso:** sem rede, sem permissão, sem espaço, token expirado. `simctl privacy revoke`, modo avião, `toxiproxy toxic add -t timeout`.
4. **Contrato:** o servidor mudou um campo, o app ainda espera o antigo; evento emitido que ninguém escuta. `map_realtime.py` lista os dois lados.

## Heurística SFDIPOT (Bach)

Antes de fechar a lista de casos, passe por Structure, Function, Data, Interfaces, Platform, Operations, Time (`data/tours.csv` TR16 a TR22). A pergunta que mais rende em app de dois papéis é **Time**: ordem de eventos, relógio errado, timeout de 10 s do push, expiração de sessão no meio.

## Tours (Whittaker)

Cada tour é um jeito de andar pelo app procurando um tipo de bug. Os que mais acham em mobile: After-hours (background), Obsessive-compulsive (repetir), Saboteur (tirar recurso), FedEx (seguir o dado até o outro papel), Supermodel (layout, fonte grande, escuro). Lista completa em `data/tours.csv`.

## O que não fazer

- **Não** rodar a suíte inteira de novo depois de cada ajuste. Regressão é o fluxo tocado mais o fluxo principal.
- **Não** confiar em "passou no simulador" para push, câmera, Keychain pós-reinstall ou rede móvel: isso é aparelho físico ou TestFlight (`10-testflight-e-crashes.md`).
- **Não** declarar "sem bug" quando o teste não rodou. "Não testado" é um resultado válido e vai no relatório.
- **Não** testar com dado de produção. Usuários de teste por papel, servidor local ou staging.

## Oráculos: como saber que está errado

Um teste sem oráculo é um passeio. Para cada caso, antes de rodar, escreva o esperado em uma linha:
- **Contagem:** "um registro no banco", "um toast", "um broadcast" (`B01`, `B07`).
- **Estado final:** "mesma tela, dado atualizado" (`B15`), "lista sem fantasma" (`B48`).
- **Tempo:** "resposta em menos de 1 s [medido]" (faixas da NN/g: 0,1 s, 1 s, 10 s).
- **Sem exceção:** `log stream --predicate 'process == "App"'` sem `Fatal`, `Unhandled`, `ExceptionsManager`.
- **Visual:** diff contra a baseline abaixo do limiar (`magick compare`).

Resultado só é bug quando viola o oráculo. "Parece estranho" vira observação, não P1.
