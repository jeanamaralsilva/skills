# Fluxo no Pencil (pen.dev)

Quando a entrega é visual, o Jean quer ver o fluxo, não só as telas: **onde tocar e para onde vai**. Cada fluxo vira um frame no canvas com as telas em ordem, um marcador numerado sobre cada ponto de toque e uma seta até a tela de destino.

Antes da primeira chamada, leia a skill do Pencil: `pencil__read_skill()` e depois `read_skill({path: "execute.md"})`. As regras de lá valem: `name` em todo nó, `placeholder: true` enquanto trabalha, nada solto na raiz do documento.

## Estrutura

```
Fluxo: <nome>                 frame raiz, layout none, fundo neutro
├── Título + legenda          "1 Toque em Iniciar treino → Execução"
├── Tela 1 ... Tela N         cópias ou instâncias das telas, 390x844, lado a lado, gap 160
├── Hotspot 1 ... N           círculo 28px numerado, cor de destaque, sobre o elemento tocável
└── Seta 1 ... N              path do hotspot até a borda esquerda da tela destino
```

Regras:
- Telas da esquerda para a direita, na ordem do caminho feliz. Caminho alternativo (erro, vazio) vai numa segunda linha, abaixo da tela onde ele nasce.
- **O número do hotspot é o mesmo número da linha da legenda.** A legenda diz o gesto e o destino: "2 Arraste a série para a esquerda → Remover".
- Gesto que não é toque (swipe, long press, pull to refresh) é escrito na legenda, e o hotspot ganha o ícone do gesto.
- Estados da mesma tela (loading, vazio, erro) ficam empilhados abaixo dela, sem seta: são a mesma tela.
- Cor do hotspot e da seta fora da paleta do app, para nunca ser confundida com UI.

## Snippet base

Rode num `execute`. Ele recebe as telas já existentes (ids) e os passos. Ajuste `steps` para cada fluxo.

```js
const screens = ["<idTela1>", "<idTela2>", "<idTela3>"]
const steps = [
  {from: 0, to: 1, x: 195, y: 780, label: "Toque em Iniciar treino"},
  {from: 1, to: 2, x: 330, y: 420, label: "Toque em Registrar carga"},
]
const W = 390, H = 844, GAP = 160, TOP = 140, HOT = "#FF3B6B"
const pos = FindEmptySpace({width: screens.length * (W + GAP), height: H + 260, padding: 120})
flowId = Insert(document, {type: "frame", name: "Fluxo: Execução de treino", layout: "none", x: pos.x, y: pos.y,
  width: screens.length * (W + GAP) + GAP, height: H + TOP + 120, fill: "#F4F4F5", placeholder: true})
Insert(flowId, {type: "text", name: "Título", x: GAP, y: 40, content: "Fluxo: Execução de treino", fontFamily: "Inter", fontSize: 28, fontWeight: "700", fill: "#18181B"})
Insert(flowId, {type: "text", name: "Legenda", x: GAP, y: 84, fontFamily: "Inter", fontSize: 15, fill: "#3F3F46",
  content: steps.map((s, i) => `${i + 1}  ${s.label} → ${Get(screens[s.to]).name}`).join("     ")})
const left = i => GAP + i * (W + GAP)
screens.forEach((id, i) => Copy(id, flowId, {name: `Tela ${i + 1}`, x: left(i), y: TOP}))
steps.forEach((s, i) => {
  const hx = left(s.from) + s.x, hy = TOP + s.y, tx = left(s.to), ty = TOP + H / 2
  const w = tx - hx, h = ty - hy
  Insert(flowId, {type: "path", name: `Seta ${i + 1}`, x: hx, y: Math.min(hy, ty), width: w, height: Math.abs(h) || 2,
    viewBox: [0, 0, w, Math.abs(h) || 2], stroke: HOT, strokeWidth: 3, strokeLinecap: "round",
    geometry: h >= 0 ? `M0 0 C ${w / 2} 0 ${w / 2} ${h} ${w} ${h}` : `M0 ${-h} C ${w / 2} ${-h} ${w / 2} 0 ${w} 0`})
  const dot = Insert(flowId, {type: "frame", name: `Hotspot ${i + 1}`, x: hx - 14, y: hy - 14, width: 28, height: 28,
    cornerRadius: 14, fill: HOT, justifyContent: "center", alignItems: "center"})
  Insert(dot, {type: "text", name: "Número", content: String(i + 1), fontFamily: "Inter", fontSize: 14, fontWeight: "700", fill: "#FFFFFF"})
})
Update(flowId, {placeholder: false})
TakeScreenshot([flowId])
```

`x` e `y` de cada passo são a posição do elemento tocável dentro da tela de origem. Leia com `Get(tela, (n, c) => n.name === "Botão Iniciar" && Print(c.bounds))` em vez de chutar.

## Conferência

- Na screenshot, todo hotspot fica em cima de um elemento tocável real e toda seta termina numa tela.
- A legenda tem uma linha por hotspot, com o mesmo número.
- Nenhuma tela ficou cortada (`Get(flowId, (n, c) => c.problems && Print(n.name, c.problems))`).

## Resposta no chat

Depois de desenhar, a resposta é curta: o nome do frame, quantos passos tem o fluxo e a recomendação. O fluxo está no canvas, não repita ele em texto.
