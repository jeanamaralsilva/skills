# 03. Ataques funcionais

Fontes em `_pesquisa.md` §1.5 e §2.

## Dado
- 0, 1, muitos; primeiro, meio, último; Goldilocks (grande demais, pequeno demais, normal).
- Texto: 200 caracteres, acentos, emoji, só espaços, espaço no fim, colar com quebra de linha.
- Número: 0, negativo, vírgula e ponto, colar "R$ 1.234,50", limite máximo.
- Máscaras BR: telefone com e sem 9, CPF, moeda; apagar do meio; autofill.
- Unicidade: mesmo e-mail, mesma entidade com caixa trocada, mesmo agendamento no mesmo horário.
- Ciclo de vida: criar → ver em outra tela → editar → apagar → conferir que sumiu de todo lugar.

## Tempo
- Agendamento de hoje que já passou, que começa em 5 min, às 23:30 (vira outro dia em UTC), na virada do mês.
- App aberto na virada da meia-noite. Aparelho em outro fuso (Manaus).
- Coisa que expira: código, convite, vínculo ou assinatura no último dia, sessão (token).

## Ciclo de vida e interrupção
- Background no meio do envio e volta; matar o app no meio do fluxo e reabrir.
- Central de notificações puxada com formulário aberto (estado `inactive`).
- Logout e login de outra conta/papel no mesmo aparelho: nada pode vazar.

## Rede
- Offline na abertura; cair no meio do envio; voltar. Erro tem mensagem humana e botão de tentar de novo.
- Retry de POST: conte no banco se nasceram dois.

## Duplo toque
Dois toques rápidos em todo botão que cria ou cobra (salvar, agendar, aceitar, pagar, concluir). Confira no banco.

## Navegação
- Voltar leva para onde o usuário espera (de onde veio, não para a raiz).
- Deep link frio e quente, sem login e com o papel errado.
- Aba trocada no meio de um formulário: perdeu o que digitou?

## Permissões
Negar e revogar depois (contatos, câmera, notificações, localização): o app continua útil e explica.

## Multiusuário
Papel A muda, papel B vê (e vice-versa) sem matar o app. Dois atores no mesmo dado ao mesmo tempo. Ator B por API: se a skill `ceo-testes` estiver instalada, use o ator dela (`phx_actor.mjs`); senão, curl com o token do ator B (login por API, `Authorization: Bearer <token>`) e confira a mudança no app aberto.

## API (sem simulador)
- BINMEN: Boundary, Invalid, Null, Method, Empty, Negative em cada campo.
- VADER: Verbs, Auth (token de outro usuário, outro papel, sem token), Data, Errors (500 é bug sempre), Responsiveness.
- Tente ler e alterar recurso de outro usuário (mesmo papel e papel diferente) pelo id: 404/403, nunca 200. 401 também é bug (o app acha que a sessão expirou).
- Contrato: rode os schemas do app (zod/io-ts) contra a resposta real de cada GET que o app usa. Falha de parse vira tela "não encontrado" ou vazia.
- 500 é sempre bug: tamanho > coluna, `null` explícito, tipo errado, número que estoura a coluna.
