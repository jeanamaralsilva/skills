# Analisar bug por vídeo, print e relato

O cliente manda um vídeo de 40 s e diz "travou". O trabalho é transformar isso numa reprodução com causa, não em "vamos investigar".

## 1. Vídeo → frames

```bash
python scripts/video_frames.py bug.mp4 --out runs/frames [--threshold 0.3]
```

Gera `sheet.png` (um frame por segundo em grade 4x4: leia primeiro, é o vídeo inteiro numa imagem) e `sc_NNN.png` nas mudanças de cena com o timestamp de cada uma. Mudança de cena é toque, navegação, sheet abrindo, erro aparecendo, crash. Depois, `Read` em cada PNG. Limiar 0,3 pega transições de tela; 0,15 pega sheets e toasts; abaixo disso vira ruído de scroll.

Equivalentes à mão (ffmpeg 8+ removeu `-vsync`; use `-fps_mode`):
```bash
ffmpeg -i bug.mp4 -vf "select='gt(scene,0.3)',showinfo" -fps_mode vfr runs/f%03d.png 2>&1 | grep pts_time
ffmpeg -i bug.mp4 -vf "fps=1,scale=360:-1,tile=4x4" -frames:v 1 runs/sheet.png
ffmpeg -ss 00:00:12 -to 00:00:18 -i bug.mp4 -c copy runs/trecho.mp4          # só o trecho do bug para o relatório
ffprobe -v error -show_entries format=duration -of csv=p=0 bug.mp4
```

O que procurar frame a frame, nesta ordem:
1. **Último estado bom** e **primeiro estado ruim**: o bug está entre os dois. O timestamp vai no relatório ("00:12,4 → 00:13,1").
2. **O que o usuário fez** no intervalo: toque (dedo, highlight do botão), gesto, teclado aparecendo, troca de app (barra de status muda), notificação.
3. **Sinais na barra de status:** Wi-Fi sumiu? relógio pulou (background longo)? bateria baixa (Low Power Mode muda comportamento de rede e animação)?
4. **Estado da tela ruim:** spinner infinito (B12), tela em branco (B29, crash de render), dado velho (B09, B10), duplicata (B01, B46), layout quebrado (B33 a B35), sheet que não fecha, botão sem resposta.
5. **Texto de erro**, mesmo pequeno: toast, banner, Alert. Transcreva literalmente e procure no código (`grep -rn "texto" src/`).

## 2. Print → medidas

- Diff contra a mesma tela no simulador: `magick compare -metric RMSE cliente.png simulador.png runs/diff.png 2>&1` (saída no stderr: `53509 (0.81)`; exit 1 quando diferente). Áreas vermelhas no `diff.png` são o que mudou.
- Lado a lado para o relatório: `magick montage a.png b.png -tile 2x1 -geometry +4+4 -label '' runs/m.png`.
- Tamanho da tela do cliente: `magick identify -format "%wx%h" print.png`. 1170x2532 é iPhone 13/14; 1179x2556 é 15/16/17; 1206x2622 é Pro; 750x1334 é SE. Isso decide em qual simulador reproduzir.
- Fonte grande? Compare a altura de uma linha de texto com a do simulador em `content_size` padrão.

## 3. Relato → hipótese

"Trava às vezes", "some", "não atualiza", "mandou duas vezes" mapeiam direto em `data/bugs.csv`:

```bash
python scripts/search.py "não atualiza quando o outro envia"      # → B09, B10, B43
python scripts/search.py "enviou duas vezes"                      # → B01, B41, B24
python scripts/search.py "spinner infinito offline"               # → B12
python scripts/search.py "voltou do background e ficou parado"    # → B15, B16, B42
```

Cada linha tem `how_to_provoke` e `what_to_observe`: é o roteiro de reprodução. Rode as duas ou três hipóteses mais prováveis; a que reproduz é a causa, as outras saem do relatório.

## 4. Reprodução mínima

Reproduzido no simulador, encolha até o menor roteiro que ainda quebra (Maestro de 5 a 10 linhas ou `phx_actor` com 2 passos) e grave:

```bash
xcrun simctl io <UDID> recordVideo --codec=h264 --force runs/repro.mov &
maestro --device <UDID> test repro.yaml
kill -INT %1
```

Relatório: passo a passo, vídeo de até 15 s, timestamp, arquivo:linha da causa, correção proposta. Se não reproduziu em 3 hipóteses: relatório diz "não reproduzido", lista o que foi tentado e pede o que falta (versão do app, iOS, se estava em Wi-Fi ou 4G, horário).

## 5. Crash

Vídeo que termina com o app fechando é crash. Vá para `10-testflight-e-crashes.md`: o crash log do TestFlight ou do Organizer dá a linha exata, o vídeo dá o passo. No simulador, `~/Library/Logs/DiagnosticReports/*.ips` e `log stream --predicate 'process == "App"'` durante a reprodução.

## Fontes

- ffmpeg `select`/`scene`, `tile`, `-fps_mode`: https://ffmpeg.org/ffmpeg-filters.html#select_002c-aselect ; https://ffmpeg.org/ffmpeg-filters.html#tile ; https://ffmpeg.org/ffmpeg.html#Advanced-Video-options
- ImageMagick compare e montage: https://imagemagick.org/compare/ ; https://imagemagick.org/montage/
- Categorias de crash em apps móveis: https://ar5iv.labs.arxiv.org/html/1801.07009
