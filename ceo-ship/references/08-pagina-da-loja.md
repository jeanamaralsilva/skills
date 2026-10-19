# Página da loja: screenshots, textos e notas de versão

Consultado em 2026-10-19.

## Limites

| Item | App Store | Google Play |
|---|---|---|
| Notas de versão | What's New até 4000 caracteres | até 500 caracteres por idioma |
| Texto que muda sem nova revisão | texto promocional, até 170 | (não levantado) |
| Descrição | até 4000 | curta 80, completa 4000 |
| Título | (não levantado) | 30 |
| Palavras-chave | até 100 bytes | (não levantado) |
| Screenshots | 1 a 10 por tamanho; .jpeg, .jpg ou .png | 2 no mínimo, até 8 por tipo de aparelho; lado entre 320 e 3840 px, o maior até o dobro do menor |
| Obrigatórios | iPhone com Dynamic Island (tela média, 1179x2556 ou 1206x2622); iPad 13 polegadas (2064x2752 ou 2048x2732) se o app roda em iPad | ícone 512x512, imagem de destaque 1024x500 |

Fontes:
- Apple, textos: https://developer.apple.com/help/app-store-connect/reference/app-information/platform-version-information
- Apple, screenshots: https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications/
- Play, notas: https://support.google.com/googleplay/android-developer/answer/9859348
- Play, textos: https://support.google.com/googleplay/android-developer/answer/9859152
- Play, imagens: https://support.google.com/googleplay/android-developer/answer/9866151

`ios.supportsTablet: true` faz o app rodar em iPad e torna o screenshot de iPad obrigatório (achado `IOS07`). Se o app não foi pensado para iPad, decida com o CEO antes de subir.

## O que a revisão olha

- Screenshots mostram o app em uso, não só splash, login ou arte (2.3.3).
- Nada de nome, ícone ou print de outra plataforma (2.3.10). Print de Android na App Store é rejeição.
- Metadados batem com o app (2.3).

Fonte: https://developer.apple.com/app-store/review/guidelines/

Para escolher quais telas mostrar e a ordem (primeira impressão), use `ceo-ux`, se instalada.

## Notas de versão

Modelo em `assets/release-notes-template.md`. Regras do time (não das lojas):
- Escreva para o cliente, não para o time. "Atualização do brandbook", "módulo X em beta" e nome de ticket não dizem nada a quem usa.
- Comece pelo que a pessoa ganha. Uma linha por mudança, verbo no início.
- "Correção de bugs" sozinho não informa: diga qual problema sumiu, se o cliente sentia.
- Mesmo texto nas duas lojas, cortado para 500 caracteres no Play.
- Novidade grande também vai nas notas para revisão da Apple, com detalhe e como testar (2.3.1(a)).
