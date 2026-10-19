# Rejeição recebida

1. Leia a mensagem inteira e ache a diretriz (Apple: "Guideline 2.1", "5.1.1(v)"...; Google: nome da política).
2. Procure em `data/rejections.csv`: causa comum, correção e fonte.
3. Ache a causa no código ou no Console, com evidência (`arquivo:linha`, print do Console, dado do formulário). Não responda "corrigido" sem ter achado.
4. Decida o caminho:
   - Metadado ou formulário (screenshot, notas, App Privacy, Data safety, conta demo): corrige no Console e reenvia, sem build.
   - Código JS: pode ir por OTA só se o build em revisão já pega o update e a correção não muda o nativo (`references/05-versao-ota-ou-build.md`). Na dúvida, build novo.
   - Nativo, permissão, privacy manifest: build novo com número maior.
5. Responda ao revisor curto: o que estava errado, o que mudou, onde ver (passo a passo). Para conta demo, credenciais vão no campo próprio, não no texto.

Rejeição repetida pela mesma diretriz deixa a revisão mais lenta [fonte: https://developer.apple.com/app-store/review/guidelines/]. Não reenvie sem corrigir.

Se a rejeição parece errada, explique ao revisor com evidência antes de mudar o app. Discordar é decisão do CEO: diga o risco (mais uma rodada de revisão) e o prazo.
