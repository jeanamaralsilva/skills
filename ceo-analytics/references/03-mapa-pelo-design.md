# Mapa pelo design

## Pencil (pen.dev) via MCP

O mesmo método do `pixel-perfect`: exporte a imagem e o spec. O spec é a fonte de hex, px e tamanho de fonte. Não leia valor no olho a partir do PNG.

```
Export([frameId], "png", outPath, {scale: 2})
Export([frameId], "html-tailwind", specPath)
```

Para listar frames e entender a hierarquia, use o estado do app (`get_app_state`) antes de exportar. Cada frame vira uma linha do mapa, como no mapa pelo código.

## Figma

Sem conector do Figma nesta sessão, não finja que abriu o link. Peça ao Jean um export (PNG por frame) ou o acesso. Com os PNGs, leia as dimensões com `magick identify -format "%wx%h" arquivo.png` e trate como referência visual. Nesse caso, valores de cor e espaçamento são `[estimado]` até alguém medir.

## Lovable ou outro builder

Se o design vive num projeto Lovable (caso do WAYUP), o design **é** código: use `mcp__Lovable__list_files` e `read_file` e mapeie como em `01-mapa-pelo-codigo.md`. Para ver renderizado, abra o `preview_url` no navegador.

## Design x código

Quando existem os dois, a comparação é o achado mais valioso desta fase:

| Tela | No design | No app | Diferença |
|---|---|---|---|

Tela que só existe no design é trabalho pendente. Tela que só existe no app não passou por design e merece atenção dobrada no diagnóstico. Para medir a fidelidade de uma tela que devia ser igual, chame `pixel-perfect`: ele dá o número, e você não opina "parece igual".
