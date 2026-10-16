# 05. Aprendizados: modelo

Os aprendizados são do projeto, não da skill: a skill instalada é compartilhada entre projetos e é sobrescrita no update. Por isso o log fica no repo do app, em `.ceo/aprendizados.md`.

**Primeira rodada num repo:** se `.ceo/aprendizados.md` não existe, copie este modelo para lá (só o bloco abaixo) e preencha "Onde este app costuma quebrar" com os padrões de `06-aprendizados-exemplo.md` que se aplicam à stack. Eles são semente: viram linha do projeto só depois de testados nele.

Decida com o dono se `.ceo/` entra no git (o time aprende junto) ou fica em `.git/info/exclude` (só local).

Formato de cada linha: `- [AAAA-MM-DD] padrão → onde procurar da próxima vez (evidência)`.
- **padrão:** o defeito em termos que se repetem em outra tela, não o bug de um dia.
- **onde procurar:** a busca ou o passo que acha o próximo (arquivo, grep, tela, ação).
- **evidência:** print, PR ou sessão de onde veio. Sem evidência, não entra.

Se um tipo de defeito aparece 2 vezes, ele vira regra do projeto (um grep ou lint em `.ceo/` ou no CI do app, não no `ugly_scan.py` instalado, que é sobrescrito no update; regra que serve a qualquer app vira PR no repo da skill) ou charter novo nas notas do projeto.

---

```markdown
# Aprendizados de bug deste app

Formato: `- [AAAA-MM-DD] padrão → onde procurar da próxima vez (evidência)`.

## Onde este app costuma quebrar

## Falsos positivos que já enganaram

## Atalhos de ambiente que funcionam

## Charters que renderam mais
```
