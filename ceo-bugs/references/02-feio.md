# 02. O que o cliente acha feio

Feio é bug pelo oráculo Image (parece amador) ou Product (inconsistente consigo mesmo). Fontes em `_pesquisa.md` §3.

## Inspeção por tela (olhe o print, não o código)
- **Texto:** cortado sem reticências, sobreposto, quebra feia (palavra sozinha na linha), inglês no meio do português, maiúsculas misturadas entre botões iguais, plural errado ("1 aulas", "0 aula"), acento faltando, erro técnico ("500", "undefined", "Invalid date", "NaN", "null").
- **Números e datas:** dinheiro sem "R$ 1.234,56", ponto decimal, data americana, mês ou dia em inglês, AM/PM, fuso (aula às 3h que era 0h).
- **Layout:** alinhamento torto entre cards iguais, espaçamento diferente para a mesma coisa, conteúdo sob notch/status bar/home indicator, botão atrás do teclado, cartão que estoura com nome longo, ícone desalinhado do texto.
- **Estados:** tela branca antes do conteúdo, pulo de layout quando carrega, spinner eterno, vazio sem explicação nem ação, erro sem caminho de saída, loading que some e volta (flicker).
- **Toque:** alvo menor que 44 pt, sem feedback ao tocar, botão que parece desabilitado mas funciona (ou o contrário).
- **Consistência:** o mesmo conceito com nomes diferentes ("aluno"/"cliente", "pacote"/"contrato"), o mesmo botão com cores diferentes, voltar com ícone diferente em cada tela.

## Variações obrigatórias de print
Fonte máxima (`xcrun simctl ui <udid> content_size accessibility-extra-extra-extra-large`), tela pequena (iPhone SE), dado longo, lista vazia, lista com muitos itens. Fixe a status bar para comparar (`simctl status_bar <udid> override --time 9:41`).

## O que ler no código (o scanner não pega)
- `Text` com nome de pessoa sem `numberOfLines` em card e linha de lista.
- Largura/altura fixas em container com texto (quebra com fonte grande).
- `toFixed` ou concatenação para dinheiro; `format("MMM")` sem locale pt-br.
- `catch (e) { setError(e.message) }`: mensagem crua de rede na tela.
- Query sem ramo de erro (tela em branco) e lista sem `ListEmptyComponent`.
- Submit sem `disabled` durante o envio.
