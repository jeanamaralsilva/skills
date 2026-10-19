# Inventário de dados pessoais: <app>

Registro simplificado das operações de tratamento (LGPD art. 37) [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm]. Agente de pequeno porte pode manter registro simplificado (Res. CD/ANPD nº 2/2022) [fonte: https://www.in.gov.br/en/web/dou/-/resolucao-cd/anpd-n-2-de-27-de-janeiro-de-2022-376562019]. No GDPR, art. 30 [fonte: https://publications.europa.eu/resource/celex/32016R0679].

Atualizado em: <data> por <papel>. Gerado a partir de `scripts/pii_scan.py` e completado à mão. **Nunca valor de dado pessoal neste arquivo.**

- Controlador: <razão social>
- Encarregado ou canal do titular: <contato de função>
- Países dos usuários: <BR | UE | ...>  Menores usam? <não | provável | sim>

## Tratamentos

| Dado (categoria) | Sensível? | Finalidade | Base provável (confirmar com advogado) | Onde fica (`arquivo:linha` ou sistema) | Quem acessa | Vai para (SDK, fornecedor, país) | Retenção | Exclusão na conta? |
|---|---|---|---|---|---|---|---|---|
| e-mail | não | login e avisos da conta | execução de contrato | `users.email` | suporte (leitura) | provedor de e-mail (<país>) | enquanto a conta existir | sim |
| | | | | | | | | |

## Fornecedores (operadores)

| Fornecedor | O que recebe | Para quê | País | Contrato ou DPA? | Fonte do que coleta |
|---|---|---|---|---|---|
| | | | | | |

## Não verificado

- <sistema, painel ou fornecedor que ninguém conferiu>
