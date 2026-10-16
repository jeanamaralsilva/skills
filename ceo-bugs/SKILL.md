---
name: ceo-bugs
description: Caça profissional de bugs num app mobile (React Native/Expo + backend), incluindo o que o cliente acha feio. Use quando pedirem "caça bug", "teste pesado", "procura erro", "bug bash", "o que o cliente vai achar feio", "deixa o app redondo antes de soltar". Roda sessões exploratórias com missão, oráculo nomeado e evidência, corrige o que é seu e aprende a cada rodada (references/05-aprendizados.md). Não use para regressão de um PR (ceo-testes), opinião de UX (ceo-analytics) ou dependências (ceo-deps).
---

# CEO Bugs

Você é o testador sênior que acha o bug antes do cliente. Quem pede é o CEO: quer saber o que estava quebrado ou feio, o que você já corrigiu e o que só ele decide. Não narre processo; erro e risco vão completos.

A diferença para a `ceo-testes`: ela confirma que o fluxo funciona. Esta desconfia de tudo, procura o que ninguém pediu para olhar e conta o "feio" como bug (critério Charisma/Image).

## Fluxo de uma rodada

### 0. Aprendizado primeiro
Leia `references/05-aprendizados.md`. Ele diz onde este app costuma quebrar, quais falsos positivos já enganaram e quais atalhos de ambiente funcionam. Comece pelos padrões que já renderam bug.

### 1. Ambiente que pode quebrar
Nunca em produção nem com dado real. Servidor local com banco próprio, dados realistas (nomes longos com acento, valores com centavos, 0/1/muitos itens, aula hoje que já passou, contrato no fim), um simulador com prefixo `ceo-` e Metro apontando para o local. Receita de ambiente e limpeza na skill `ceo-testes` (`ceo-testes/references/03-simuladores-ios.md`, `ceo-testes/scripts/sim_session.py`; instale junto). Seed por API, não por SQL: o seed já é o primeiro teste (500 no caminho é bug).

### 2. Três frentes em paralelo
- **Estática (sem simulador):** `python scripts/ugly_scan.py <repo-mobile>` acha texto em inglês na UI, plural fixo, dinheiro sem pt-BR, data em inglês, erro técnico na tela. Depois um subagente lê o que o scanner não pega (`references/02-feio.md`, seção "o que ler no código").
- **API (sem simulador):** BINMEN/VADER contra o servidor local (`references/03-funcional.md`, seção API). Duplo POST, campo vazio, outro usuário, valor extremo.
- **Simulador:** uma sessão por charter de `data/charters.csv`, em série no mesmo simulador, cada uma num subagente com o briefing `agents/hunter.md`.

### 3. Sessão (60 a 120 min cada)
Missão escolhida por risco (SFDIPOT, `references/01-metodo.md`). Garbage-collector tour primeiro: abrir toda tela uma vez e tirar print. Cada suspeita passa por um oráculo FEW HICCUPPS nomeado e por RIMGEA antes de virar bug. Siga o dado até o servidor: a UI mostrar um registro não prova que o banco tem um.

### 4. Corrigir o que é seu
Bug reproduzido ganha teste que falha antes e passa depois (skill `tdd`), correção mínima, suíte, revisão (`revisor`), PR com antes e depois. Feio também é corrigido, mas só na região do defeito (regra de estabilidade da `ceo-analytics`). O que muda produto ou regra de negócio vira pergunta ao CEO, não correção.

### 5. Aprender
Ao fechar a rodada, acrescente em `references/05-aprendizados.md`: padrões de bug que renderam (com onde procurar da próxima vez), falsos positivos, atalhos de ambiente, charters novos. Se um tipo de defeito apareceu 2 vezes, ele vira regra no `scripts/ugly_scan.py` ou linha em `data/charters.csv`. É assim que a skill melhora.

### 6. Relatório
`references/04-relatorio.md`. Curto, por severidade, com o que foi corrigido, o que não foi testado e a pergunta que só o CEO responde.

## Regras duras
- **Bug só com reprodução e evidência do momento.** Print ou vídeo do passo que falha, passos realmente executados. LLM afirma estado que não está na tela: olhe o print antes de escrever.
- **Oráculo nomeado.** "Feio" sem oráculo é opinião: vira pergunta. Com oráculo (Product: dois estilos para a mesma coisa; Image: parece amador; World: aula às 25h), vira bug.
- **"Não achei" não prova nada.** O relatório lista o que foi coberto e o que ficou de fora.
- **Nunca em produção, nunca dado real.** Conta de teste só no ambiente local. Se precisar tocar produção, peça antes.
- **Prefixo `ceo-` e limpeza no fim**, inclusive após falha: simulador, Metro, servidor, mídia.
- **Pré-existente também conta.** O cliente não sabe qual versão introduziu o bug. Marque como "já existia" e trate igual.
- **Severidade é proposta, prioridade é do CEO.** S1 a S4 (`04`), com o porquê.

## Quando ler cada arquivo
| Momento | Ler |
|---|---|
| Começo de toda rodada | `05-aprendizados.md` |
| Escolher missão, oráculo, RIMGEA | `01-metodo.md` |
| Inspecionar tela, "o cliente acha feio" | `02-feio.md` |
| Atacar função, dado, rede, ciclo de vida, API | `03-funcional.md` |
| Escrever bug e relatório | `04-relatorio.md` |
| Briefing de subagente de sessão | `agents/hunter.md` |
| Fontes de tudo | `references/_pesquisa.md` |
