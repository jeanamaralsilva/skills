# Navegação e densidade: menos camadas antes do dado

O erro mais comum em painel, admin e tela de gestão não é visual: é estrutural. Três camadas de cabeçalho, abas dentro de abas, o mesmo rótulo repetido, uma coluna inteira dizendo a mesma coisa em todas as linhas. O usuário rola meia tela antes de ver o primeiro número. Esta referência é a rubrica para isso; a ferramenta é `scripts/nav_audit.py`.

## Como auditar

Transcreva o que a tela mostra, de cima para baixo, e passe pelo script:

```bash
python scripts/nav_audit.py - <<'EOF'
title: Financeiro - Auditoria
L1: Faturamento do mês | Vínculos | Resumão
L2: Faturamento do mês | Liberados 0 | Inadimplentes 137 | Cancelados 109
L3: Todos 751 | Sem diferença 289 | Com diferença 462
heading: Setembro de 2026
col Motivo: Posse sem cobrança | Posse sem cobrança | Posse sem cobrança
EOF
```

`L1`, `L2`... são linhas de abas na ordem em que aparecem; `filters:` para chips que já são visualmente filtros; `col Nome:` para qualquer coluna cujos valores dê para ler no print. Ele não olha pixel; você transcreve, ele julga. Saída: regra, severidade, detalhe e correção, com o id da heurística (H21 a H27) e do anti-padrão (AN01 a AN05).

## Regras

| Regra | O que pega | Por quê | Correção |
|---|---|---|---|
| **Uma linha de abas** (H21, AN01) | duas ou mais linhas de abas empilhadas | o indicador de seleção fica ambíguo e a memória espacial quebra | o nível de cima vira sidebar ou página; o de baixo vira segmented control com nome diferente; ou um dos dois some |
| **Rótulo uma vez por tela** (H22, AN02) | mesmo texto no título e numa aba, ou em dois níveis | cada repetição é uma leitura sem informação nova | o nível de baixo diz o que acrescenta ("Clientes", não "Faturamento do mês" de novo) |
| **Aba não é filtro** (H23, AN03) | as contagens das abas somam o total: é a mesma tabela filtrada | aba promete conteúdo diferente; filtro promete o mesmo conteúdo reduzido | chips ou segmented control colados na tabela, com contagem; aba só para entidade diferente (Clientes, Vínculos, Resumo) |
| **Rótulo curto** (H24) | aba com 3+ palavras ou termo interno | NN/g: 1 a 2 palavras; mais que isso é sinal de que a escolha é complexa demais para aba | renomear ou reagrupar |
| **Aba vazia** (H25) | contagem 0 | ocupa espaço e atenção sem conteúdo | esconder quando vazia, ou mostrar por que existe |
| **Coluna constante** (H26, AN04) | mesmo badge em todas as linhas visíveis | o valor é do filtro, não da linha | mover para o filtro ativo ou cabeçalho; na linha só quando difere |
| **Ícone sem legenda** (H27) | triângulo de alerta ao lado do nome sem tooltip ou coluna | o usuário adivinha | tooltip no hover, legenda no cabeçalho, ou coluna "Motivo" que já explica |
| **Cabeçalho em cascata** (AN05) | 5+ blocos (título, abas, subabas, filtros, h2) antes da primeira linha | o dado fica abaixo da dobra | uma faixa: título com período e métrica principal; filtros e busca na linha da tabela |

## Como reduzir, na prática

Ordem de cortes, do que mais devolve espaço ao que menos:

1. **Junte título e período.** "Auditoria de setembro de 2026" numa linha, com a métrica principal ao lado ("751 clientes · R$ 2,12 mi a faturar"). O h2 separado some.
2. **Decida o que é aba.** Entidades diferentes (Clientes, Vínculos, Resumo) são abas. Estados da mesma entidade (Liberados, Inadimplentes, Cancelados) são filtro ou segmented control na linha da tabela, com contagem.
3. **Filtros numa linha só, colados na tabela**, com a busca à direita. Um segmented control para a partição (Todos / Sem diferença / Com diferença) e chips para o status.
4. **Tire da linha o que é igual em todas.** "Posse sem cobrança" em todas as linhas vira o nome do filtro ativo ou um subtítulo da tabela; a coluna Motivo volta a existir só quando os motivos diferem.
5. **Explique o ícone** ou troque por uma coluna. Se o triângulo significa "tem diferença", a coluna Δ em vermelho já diz isso: o ícone é redundante.
6. **Alinhe números à direita, com a mesma largura** (tabular figures), e cor só no Δ. O olho compara colunas, não lê células.

Antes e depois esperados: 8 blocos acima da tabela viram 3 (título com período e métrica; abas de entidade; linha de filtros e busca). A primeira linha de dado sobe uns 200 px em desktop.

## Mobile

As mesmas regras, com dois agravantes: largura e polegar. Tab bar inferior é o único nível de abas; qualquer segundo nível dentro de uma aba vira segmented control (iOS) ou chips roláveis (Android), nunca uma segunda tab bar. Filtros entram num sheet quando passam de 3. Tabela vira lista de cards com os 2 ou 3 números que decidem, e o resto no detalhe.

## Quando a camada extra se justifica

- O nível de cima é navegação entre páginas e o de baixo é conteúdo da página, **e** eles têm aparência diferente (sidebar + abas; abas + segmented). NN/g alerta só contra misturar os dois no mesmo controle.
- A tabela tem 20+ colunas e o filtro por status muda as colunas mostradas: aí é conteúdo diferente, e aba cabe.
- Produto denso para operador treinado (ERP, tesouraria), medido com o operador: densidade alta pode ser o pedido. Mesmo assim, rótulo repetido e coluna constante não têm defesa.

## Fontes

- NN/g, Tabs, Used Right (2024, revisado 2026): uma linha de abas, rótulos de 1 a 2 palavras, não misturar navegação e conteúdo no mesmo controle, aba não serve para comparar: https://www.nngroup.com/articles/tabs-used-right/
- NN/g, Filters vs. Facets: filtro reduz o mesmo conjunto; só vale quando bate com a dimensão que o usuário usa: https://www.nngroup.com/articles/filters-vs-facets/
- NN/g, 10 heurísticas (visibilidade, reconhecimento em vez de memória, minimalismo): https://www.nngroup.com/articles/ten-usability-heuristics/
