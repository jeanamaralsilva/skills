# Arquitetura e acoplamento

A pergunta é: **se essa lib sumir amanhã, quantos arquivos eu reescrevo?**

## Medir

```bash
python scripts/deps_scan.py <repo> --spread 10
```

Conta quantos arquivos de produção (testes fora) importam cada lib de terceiro. Frameworks de base (react, react-native, expo-*, phoenix, ecto, oban) ficam fora: trocar framework é outro projeto. O número é heurística, não métrica formal.

| Situação | Leitura |
|---|---|
| Lib de terceiro em muitos arquivos de produção, sem wrapper | acoplamento espesso: trocar ou atualizar com breaking change custa caro |
| Lib atrás de um módulo próprio (`lib/app/mailer.ex`, `src/api/client.ts`) | acoplamento fino: troca em um lugar |
| SDK de nuvem (AWS, Firebase) espalhado | vendor lock-in |

Regra (phxagents Iron Law 20, vale para qualquer stack): **encapsule a API de lib de terceiro num módulo seu.** Padrões: Adapter, Repository, Anti-corruption layer. O ACL custa uma camada a mais e não deve ter regra de negócio.

Exemplos reais (app Expo + server Phoenix, out/2026):
- mobile: `@lodev09/react-native-true-sheet` direto em 42 arquivos; `sonner-native` em 29. Um wrapper `Sheet` e um `toast()` próprios reduzem cada troca futura a um arquivo.
- server: `Guardian` em 6 arquivos e `Req` em 4. Aceitável; vale centralizar o `Req` num cliente com timeout e retry configurados.

## Elixir: acoplamento de compilação

```bash
mix xref graph --label compile-connected --format stats
mix xref graph --label compile-connected --format cycles --fail-above 0
```

Dependência de compilação transitiva faz um arquivo mudado recompilar metade do app. `boundary` (`use Boundary, deps: [...], exports: [...]`) proíbe chamadas entre contextos que não deveriam se conhecer.

## Tamanho

- Expo: `EXPO_ATLAS=true npx expo export` e depois `npx expo-atlas .expo/atlas.jsonl`. O `.jsonl` contém código-fonte: não compartilhe.
- Lib pesada para uma função pequena (moment para formatar uma data) é achado P2.

## Multi-repo (server + mobile)

O que quebra entre repos não aparece em nenhum audit de pacote:

| Risco | Como checar |
|---|---|
| Contrato da API mudou e o app não acompanhou | OpenAPI versionado e `oasdiff breaking base.yaml rev.yaml`; sem OpenAPI, compare os schemas do mobile (zod) com os do server (changesets) e os testes de contrato |
| App antigo em produção (version skew) | o server precisa aceitar versões antigas ou existir versão mínima + atualização forçada (Android: Play In-App Updates immediate; iOS: tela própria) |
| Mesma regra validada diferente nos dois lados | um lado aceita o que o outro recusa; comparar schemas |
| Upgrade coordenado | mudança que exige deploy do server antes do app vira item de pendência com ordem |

Se o mobile já tem teste de fixtures da API (ex.: `src/api/__tests__/`), é o lugar para ancorar o contrato.
