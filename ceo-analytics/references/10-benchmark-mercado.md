# Benchmark de mercado, só com fontes gratuitas

O produto do benchmark é **padrão + trade-off + evidência de que usuários gostam**, não um mood board. Cinco prints bonitos não decidem nada. O que decide é: quatro produtos resolveram a parte difícil desta tela de três formas, cada uma custa isso, e usuários elogiam aquela.

Todas as fontes abaixo foram testadas por fetch em 30/09/2026. Tabela completa com URL: `data/market-sources.csv` (M01 a M21).

## Ordem de consulta

### 1. Por dentro primeiro

O próprio app: a mesma solução pode já existir noutra tela. Se o repo for INFLEET, `infleet-herads/references/benchmark.md` e o censo de telas do HeraDS. Metade das vezes o benchmark termina aqui: "é variante do que já temos".

### 2. Princípios

NN/g, Laws of UX, UI Patterns e Baymard (M01 a M04). Eles abrem com texto completo.

### 3. Regras da plataforma

- **Apple HIG em JSON:** `developer.apple.com/tutorials/data/design/human-interface-guidelines/<slug>.json`. A página HTML vem vazia.
- **Material:** os `.md` do repo `material-components-android` ou o Android Developers. O m3.material.io vem vazio.

### 4. Checklist da tela

`checklist.design/pages/<tela>` (M08): itens essenciais, recomendados e opcionais.

### 5. Concorrentes e referências do domínio

- **Página da App Store e do Google Play** (M09, M10). Trazem prints oficiais, nota, contagem e reviews. Para telas de app mobile, é a melhor fonte aberta que sobrou.
- **Help center e páginas de recurso do produto**, que descrevem o fluxo com print (ex.: hevyapp.com/features).
- **Apps open source** de `data/reference-apps.csv`, lidos por `raw.githubusercontent.com` (M20).

### 6. Voz do usuário

- **Reviews** da App Store (`?see-all=reviews`, cerca de 10 por página), do Google Play e do Product Hunt.
- Procure o que se repete. Uma review isolada é anedota.
- Registre o elogio e a reclamação com o link.

### 7. Excelência

Apple Design Awards, Google Play Best of (post no blog.google) e Webby Awards de apps (M12 a M14).

### 8. Código real

- **grep.app:** `grep.app/api/search?q=<Componente>` mostra como o mercado usa uma lib.
- **API de busca do GitHub:** `api.github.com/search/repositories?q=...` acha bibliotecas e apps.

## O que não funciona sem login (não perca tempo)

Behance, Reddit, Mobbin (além da home), Screenlane, a busca do Dribbble, Pinterest, m3.material.io, Sensor Tower e a busca web do GitHub.

Se a tarefa depende deles, diga no relatório que não foram consultados. Se o Jean tiver prints ou um navegador logado, peça.

## Estudos sobre o que usuários gostam (use com o recorte certo)

- **Material 3 Expressive:** 46 estudos, 18 mil pessoas (`05-plataformas.md`).
- **Reviews de loja:** numa análise de mais de 160 mil reviews do Google Play e da App Store, usabilidade é a maior preocupação ligada a UI. https://jit.ndhu.edu.tw/article/view/2938
- **Gamificação e streak (fitness):**
  - Milkman et al. (Nature, 2021): 61 mil membros de academia. A melhor intervenção foi recompensar a **volta depois de faltar**. Só 8% dos efeitos duraram depois de 4 semanas.
  - Patel et al. (JAMA IM, 2019): só a competição manteve efeito no acompanhamento.
  - Silverman & Barasch: quebrar um streak leva ao abandono. Ofereça outra meta em vez de lembrar da falha.
  - Conclusão prática: streak ajuda pouco e pode punir. Prefira recompensar a volta.

## Comunidade

Reddit não abre; Hacker News abre pela API. Como pesar comentário contra poll e estudo: `15-comunidade-e-ecossistema.md`.

## Brief para o subagente

Use `agents/market-researcher.md`. Preencha o problema da tela em uma frase e o público.

## Saída

```
| Produto | Como resolve a parte difícil | Custo/trade-off | Evidência de que usuários gostam | Link |
```

Mais uma frase por proposta: qual padrão ela adota e por quê.
