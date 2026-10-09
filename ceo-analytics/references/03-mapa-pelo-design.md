# Mapa pelo design

## Pencil (pen.dev) via MCP

Exporte a imagem e o spec. O spec é a fonte de hex, px e tamanho de fonte. Não leia valor no olho a partir do PNG.

```
Export([frameId], "png", outPath, {scale: 2})
Export([frameId], "html-tailwind", specPath)
```

Para listar frames e entender a hierarquia, use o estado do app (`get_app_state`) antes de exportar. Cada frame vira uma linha do mapa, como no mapa pelo código.

## Figma

Sem conector do Figma nesta sessão, não finja que abriu o link. Peça ao CEO um export (PNG por frame) ou o acesso. Com os PNGs, leia as dimensões com `magick identify -format "%wx%h" arquivo.png` e trate como referência visual. Nesse caso, valores de cor e espaçamento são `[estimado]` até alguém medir.

## Lovable ou outro builder

Se o design vive num projeto Lovable, o design **é** código: use `mcp__Lovable__list_files` e `read_file` e mapeie como em `01-mapa-pelo-codigo.md`. Para ver renderizado, abra o `preview_url` no navegador.

## Design x código

Quando existem os dois, a comparação é o achado mais valioso desta fase:

| Tela | No design | No app | Diferença |
|---|---|---|---|

Tela que só existe no design é trabalho pendente. Tela que só existe no app não passou por design e merece atenção dobrada no diagnóstico. Para medir a fidelidade de uma tela que devia ser igual, compare os PNGs com `magick compare -metric RMSE design.png app.png diff.png` (ou a skill de fidelidade do time, se houver): o número decide, não "parece igual".
