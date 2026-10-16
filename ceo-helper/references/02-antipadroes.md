# Antipadrões

Cada um com fonte em `data/patterns.csv` (tipo `antipadrao`). Achou no código? Vira achado no relatório.

| # | Antipadrão | Por que não | Como aparece no código |
|---|---|---|---|
| 1 | Carrossel de boas-vindas genérico | Piora a percepção de facilidade, não melhora sucesso (NN/g) | Tela `Welcome`/`Intro` com `FlatList` horizontal de slides antes da home |
| 2 | Tour com 5+ passos | Conclusão cai para 25% (6 a 8) e 8% (9+) (Produktly) | Array de steps com mais de 3 itens |
| 3 | Dispara ao abrir o app ou em todo login | Material: nunca na abertura; disparo imediato converte menos (Chameleon) | `useEffect` no root layout ou logo após login |
| 4 | Repete para quem já viu ou dispensou, inclusive após reinstalar | Apple HIG e Material | Flag só em `AsyncStorage`/MMKV, sem servidor |
| 5 | Várias dicas em sequência | Dispensa mais rápido (NN/g); 1 por sessão (Material) | Vários `TipAnchor` sem fila global |
| 6 | Explicar o óbvio | NN/g: não explicar convenção | Dica no botão voltar, busca, avatar |
| 7 | Overlay que cobre ou bloqueia o alvo | Ensinar fazendo (Apple); dica não pode parecer interativa (NN/g) | Overlay com `pointerEvents="auto"` em tela cheia sem recorte tocável |
| 8 | Sem "Pular" ou Pular escondido | Apple HIG; Appcues | Só botão "Próximo" |
| 9 | Imagem ou vídeo na dica | Texto 44% contra vídeo 21% (Chameleon) | `Video`/`Image` dentro do balão |
| 10 | Sem caminho para rever | NN/g | Nenhum "Rever dicas" |
| 11 | Empty state mudo | NN/g: status + pista + ação | `ListEmptyComponent` com só "Nenhum item" |
| 12 | Veterano tratado como novato | Apple HIG | Checklist baseado em "primeiro login" e não em dados |
| 13 | Medir "viu a dica" como sucesso | Opinião: a ação de ativação é o que importa | Dashboard só com `tip_shown` |
| 14 | Balão que cobre o que a pessoa está digitando | Achado real (ex.: app de agendamento): com teclado aberto o balão do rodapé cobria o campo e os botões do fim do formulário | Balão inline sem ouvir `keyboardDidShow`; lado do balão escolhido pela medida feita com teclado aberto; formulário sem folga para rolar acima do balão |
| 15 | Passos que pedem a mesma coisa duas vezes | Achado real (ex.: app de agendamento): o cadastro do cliente já gera os horários e o passo seguinte manda "marcar horário" | Checklist montado por tela e não pelo que cada ação já resolve; confira o que o servidor marca como feito depois de cada passo |
| 16 | Guia que não abre sem dizer por quê | Achado real (ex.: app de agendamento): 4 guias dependiam de cliente cadastrado e pareciam quebrados | Passo sem pré-requisito visível; use cadeado + "Libera depois de X" no card e na lista de guias |
| 17 | Recurso de dois lados sem explicação | Achado real (ex.: app de agendamento): o profissional não sabia que a confirmação do horário chega ao cliente | Só guias de ação; inclua um bloco "Como funciona" para o que não tem tela para guiar |
