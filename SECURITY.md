# Segurança

As skills deste repo viram instruções e comandos na máquina de quem instala. Por isso:

- **Reportar uma vulnerabilidade:** use [Report a vulnerability](https://github.com/jeanamaralsilva/skills/security/advisories/new) (aviso privado do GitHub). Não abra issue pública.
- **O que conta como vulnerabilidade:** instrução em `SKILL.md`, `references/`, `agents/` ou `data/*.csv` que leve o agente a rodar comando perigoso, ler ou enviar segredo, mandar dado do projeto para fora sem pedir, ou obedecer a texto vindo do repo, da web ou do cliente; script que apaga, grava ou envia dado fora do esperado.
- **Como as skills se protegem:** todo conteúdo lido (código, PR, issue, review de loja, log, print, `.ceo/config.md` de repo de terceiros) é tratado como dado, não instrução; nada sai da máquina sem o usuário pedir; `read_only: true` do perfil do usuário não é desligado pelo repo; os scripts só usam biblioteca padrão, sem `shell=True`, e a rede só é usada em três lugares explícitos: consulta ao OSV na `ceo-deps` (com `--skip-scope` para pacotes privados), `gh` na `ceo-brief` (API do GitHub com o login do usuário) e `phx_actor` na `ceo-mobile-qa` (WebSocket para o servidor indicado).
- **Fixe a versão** se você precisa de estabilidade: instale a partir de uma tag (`npx skills add jeanamaralsilva/skills#v2.1.0`) em vez da `main`.
