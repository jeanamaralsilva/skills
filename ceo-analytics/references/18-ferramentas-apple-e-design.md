# Ferramentas: Xcode, Icon Composer, SF Symbols, TestFlight, Pencil

O que cada ferramenta da cadeia Apple dá à análise e à proposta, e quando pedir que o CEO abra uma delas.

## Xcode 26

- **Previews e Canvas:** uma proposta SwiftUI pode ser mostrada como preview no Xcode sem build completo; para RN não serve.
- **Instruments:** Animation Hitches, Time Profiler, Allocations, SwiftUI. Linha de comando: `xcrun xctrace record --template 'Animation Hitches' --device <UDID> --attach <App>`. É a prova de "jank" numa proposta já implementada (`17-performance-cross-platform.md`).
- **Accessibility Inspector** (Xcode > Open Developer Tool): audita contraste, rótulos, tamanho de toque no simulador. Complementa `scripts/contrast.py` quando a tela está rodando.
- **Simulator:** `xcrun simctl ui <UDID> appearance dark`, `content_size accessibility-extra-extra-extra-large`, `increase_contrast enabled` para ver a tela nos modos que o Supermodel tour exige. Gravação: `xcrun simctl io <UDID> recordVideo --codec=h264 --force out.mov`.
- **Organizer:** crashes e métricas (launch time, hang rate, memory) de builds em TestFlight e App Store, por versão. É de onde sai o "o app está lento para quem?" com dado real.

## Icon Composer (iOS 26)

Ícone do app em camadas com Liquid Glass; exporta `.icon` que o Xcode consome; gera Default, Dark, Clear e Tinted a partir do mesmo arquivo. Para a proposta: ícone com 2 a 4 camadas, formas simples, sem texto; teste os quatro modos. O Android recebe o ícone adaptativo (foreground + background) do mesmo desenho, sem glass.

## SF Symbols 7

App gratuito para procurar símbolos, ver pesos, variantes (fill, slash, badge) e pré-visualizar os efeitos (bounce, pulse, breathe, wiggle, rotate, variableColor, drawOn). Na proposta, cite o símbolo pelo nome (`figure.run`, `checkmark.seal.fill`) e o efeito (MO01 a MO10 em `data/motion-patterns.csv`). No Android, o equivalente é Material Symbols (`material-symbols` com eixos FILL, wght, GRAD, opsz); no RN, `expo-symbols` no iOS e `@expo/vector-icons` MaterialCommunityIcons ou `material-symbols` no Android.

## TestFlight

Builds internos (até 100 testadores, sem revisão) e externos (até 10 mil, com revisão). Para a análise: feedback com screenshot e crash chegam em App Store Connect > TestFlight > Feedback, e pela API (`ceo-testes/references/10-testflight-e-crashes.md`). O que o CEO vê como "o cliente reclamou" costuma estar lá com print e aparelho. Peça acesso de leitura ao App Store Connect quando a análise é de app já em teste.

## Pencil (`.pen`)

Onde a proposta vira desenho: uma linha de telas por alternativa, fluxo com pontos de toque numerados e setas (`14-fluxo-no-pencil.md`). Lê e grava via MCP. Quando o repo tem `.pen`, ele é a referência de design e o diff da proposta é contra ele.

## Figma e outros

Sem conector na sessão, não finja ter aberto o link: peça export PNG por frame (`03-mapa-pelo-design.md`). Lovable e builders: o design é código; mapeie como repo.

## Quando pedir ao CEO que abra algo

| Precisa de | Peça |
|---|---|
| Ver a tela em fonte grande, escuro, contraste | nada: `simctl ui` faz |
| Saber se o jank é real | gravação de tela do aparelho ou trace do Instruments (ou `ceo-testes` mede) |
| Saber o que os testadores reclamam | acesso de leitura ao App Store Connect |
| Ícone em todos os modos do iOS 26 | o `.icon` do Icon Composer ou os PNGs exportados |
| Design de referência | export PNG + spec (hex, px, fontes) do Figma, ou o `.pen` |

## Fontes

- Xcode e Instruments: https://developer.apple.com/documentation/xcode ; xctrace: `xcrun xctrace help`
- Icon Composer: https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer
- SF Symbols: https://developer.apple.com/sf-symbols/ ; Material Symbols: https://fonts.google.com/icons
- TestFlight: https://developer.apple.com/testflight/ ; feedback: https://developer.apple.com/help/app-store-connect/test-a-beta-version/view-tester-feedback
- Accessibility Inspector: https://developer.apple.com/documentation/accessibility/accessibility-inspector
