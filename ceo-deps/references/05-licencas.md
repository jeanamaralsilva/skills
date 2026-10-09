# Licenças

Não é parecer jurídico. É o filtro que separa o que pode seguir do que precisa de alguém de jurídico olhando. A política está em `data/licenses.csv` (31 identificadores SPDX, com uma coluna para SaaS e outra para app de loja).

```bash
python scripts/deps_scan.py <repo> --context mobile   # app nas lojas
python scripts/deps_scan.py <repo> --context saas     # backend/web servido
```

Lê `node_modules/*/package.json` e `deps/*/hex_metadata.config`. Sem install, use `osv-scanner --licenses .` ou diga "licenças não verificadas".

## As três decisões

| Política | Licenças | Por quê |
|---|---|---|
| allow | MIT, BSD-2/3, ISC, Apache-2.0, 0BSD, Unlicense, CC0, CC-BY | Permissivas; exigem só manter aviso e NOTICE |
| review | MPL-2.0 (no app), EPL, CDDL, BSD-4, BUSL/Elastic (no app), licença desconhecida | Copyleft fraco ou termos fora do padrão |
| deny | AGPL e SSPL em SaaS; GPL e LGPL em app de loja; CC-BY-NC sempre | AGPL §13 obriga oferecer o fonte a quem usa pela rede; a FSF considera os termos da App Store incompatíveis com a GPL (caso GNU Go, 2010); LGPL exige permitir relink e o iOS costuma linkar estático |

Expressão com OR (`MIT OR GPL-3.0`) vale a opção mais permissiva. Sem licença declarada é review, nunca allow.

## Cuidados

- **Versão exata:** MongoDB, Elastic, HashiCorp e Redis mudaram de licença entre versões. A política vale para a versão no lock.
- **Atribuição:** app de loja precisa de tela ou arquivo de licenças de terceiros para as permissivas também.
- **Assets contam:** fontes, ícones e animações (Lottie) têm licença própria; CC-BY-NC é comum em ícone grátis.
- **Elixir:** não há ferramenta oficial; `licensir` (`mix licenses`) está parado desde 2021. O `deps_scan.py` lê o `hex_metadata.config` direto.

Achado de licença deny é P0 até alguém de jurídico decidir. Não remova a lib sozinho: vira pendência do CEO.
