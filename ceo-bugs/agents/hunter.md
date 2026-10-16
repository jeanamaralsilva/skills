# Briefing do subagente de sessão (caçador)

Copie e preencha. O subagente não vê a conversa.

```
Objetivo: sessão exploratória de <tempo> min no app <nome> para achar bugs reais e defeitos visuais que o cliente nota. Missão: <charter de data/charters.csv>. Responda em pt-BR.

Ambiente pronto (não recrie): simulador <nome> UDID <udid>; Metro porta <p> (repo <caminho>, commit <sha>) apontando para servidor LOCAL <url> (banco de teste, pode criar dado). Contas: <lista e senha>. Abrir o app: <comando>. Ferramenta de UI: <argent/maestro + dicas de .ceo/aprendizados.md>. Mídia só em <pasta> com prefixo ceo-.

Como trabalhar: leia <skill>/references/01-metodo.md, 02-feio.md e 03-funcional.md. Print de cada tela visitada. Cada suspeita: reproduza 2 vezes, nomeie o oráculo, confira no servidor quando criar ou mudar dado (curl com token). Não edite código. Não toque produção.

Retorno (máx. 30 linhas): bugs (título do que o usuário vê, passos, esperado x observado, print, oráculo, severidade P0-P3, causa provável arquivo:linha se achou lendo o código), observações (sem reprodução ou opinião), o que cobriu e o que não cobriu.
```
