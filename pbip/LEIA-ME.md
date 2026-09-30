# Painel PCM (Fase 1) — Power BI, somente leitura

Formato PBIP (modelo semântico em TMDL + relatório). **Gerado sem o Power BI Desktop**, portanto **ainda não foi aberto nem atualizado por ninguém**. Trate a primeira abertura como um teste.

## Como abrir (no computador da empresa)
1. Power BI Desktop → *Arquivo → Opções → Recursos em versão prévia* → habilite **Formato de projeto do Power BI (.pbip)** e, se existir, **Armazenar modelo semântico usando formato TMDL**. Reinicie.
2. Abra `PCM_Painel.pbip`.
3. *Transformar dados → Gerenciar parâmetros* e preencha:
   - `SiteContOp` — URL do site da lista Cont_op (`…/sites/ProjetosdeServios-SS`)
   - `SiteEND` — URL do site da lista de END (`…/sites/QualidadeSAMSS`)
   - `NomeListaContOp` — título da lista (padrão `Cont_op`)
   - `NomeListaEND` — título da lista de END (padrão `Lista Recertificação`; a URL mostra `Lista Recertificao`, sem acento, **confirmar o título real**)
4. *Atualizar*. Entre com a conta corporativa quando pedir credenciais (organizacional).
5. Se a atualização acusar coluna inexistente: os nomes de coluna vêm das planilhas-cópia; no SharePoint podem ter outro nome de exibição. Ajuste a lista `Colunas` na consulta `Cont_op`. (Colunas ausentes ficam vazias em vez de derrubar a atualização; confira se o painel não está “em branco” por isso.)

## Modelo
| Tabela | Conteúdo |
|---|---|
| `Cont_op` | lista Cont_op (linhas com ID), NP/NS normalizados, `Venc_Final` = coluna de vencimento ou, se vazia, a data de `Venc.:` no texto de “Status manutenção” (`Venc_Origem` diz qual) |
| `END_ultimo` | lista END, uma linha por NP+NS normalizado, com a **maior validade** (regra confirmada). Datas inválidas ficam vazias e contadas em `Datas_invalidas` |
| `Vencimentos` | uma linha por item do Cont_op × tipo: *Manutenção FRT/EQP* e *END* (END só para itens cujo NP+NS existe na lista de END). Relacionada a `Cont_op[ID]` |
| `Faixa_Venc` | as faixas da seção 5.2 |
| `Eslinga` | **vazia** de propósito (dados ainda serão alimentados); nenhum visual a usa |

## Faixas (seção 5.2) — sempre contra HOJE
`dias = DATEDIFF(TODAY(), vencimento)`; é medida DAX, recalcula a cada abertura, **não** usa colunas gravadas.

| Faixa | dias |
|---|---|
| Vencido | ≤ −1 |
| 0 a 29 | 0…29 |
| 30 a 59 | 30…59 |
| 60 a 75 | 60…75 (dia 60 incluído) |
| > 75 (sem alerta) | ≥ 76 |
| Sem data | vazio ou ilegível |

Limites contíguos (−1|0, 29|30, 59|60, 75|76): não há valor sem faixa. Verificado em Python com os dados reais e os dias −1, 0, 29, 30, 59, 60, 75 e 76.
Não implementado: “Flexibilização” (`[CONFIRMAR]` na spec) e “dias de validade na data da operação” (opcional).

## Página “Painel PCM”
Vencimentos por faixa (por tipo) · itens por *Status Processo* · motivo de RT em avanço · segmentações *Sonda / Barco* e *Status PCM* · 2 cartões.

## Limitações conhecidas
- **Sem definição de “item ativo”.** O Cont_op guarda operações de 2021–2024; contra HOJE (30/09/2026) quase tudo aparece **Vencido** (na cópia: 1.497 de 1.499 itens com data). Use os filtros por enquanto; o correto é definir uma regra de item ativo (ex.: Status PCM, Status Processo ou data de necessidade). Isso é decisão sua; não inventei.
- “Sem data” em manutenção é grande (cópia: ~1.257 de 2.756); muitos itens não têm vencimento aplicável.
- END: só 770 de 2.756 linhas do Cont_op casam por NP+NS com a lista de END (na cópia).
- “Itens por status” usa `Status Processo` (sua escolha); linhas sem status aparecem como “(sem status)”.
- O relatório está em formato **PBIR legado** (`report.json` único). O Desktop abre e converte. Se acusar erro, abra só o modelo e recrie os 3 gráficos com os campos da tabela acima.
