# Regras de normalização como passos de Power Query

Cole cada `.pq` como **consulta em branco** com o nome do arquivo (ex.: `fNormalizaNP`). Aplicação por lista:

| Lista | Passo (Transformar coluna → Adicionar coluna personalizada) | Resultado |
|---|---|---|
| Catálogo / PCM / Cont_op / END | `NP_Norm = fNormalizaNP([NP])` | NP sem NBSP, espaço sobrando, minúsculas |
| Cont_op / END / Equipamento_NS | `NS_Norm = fNormalizaNS([NS])` e `NS_ForaDoPadrao = fNSForaDoPadrao([NS])` | limpeza de espaços + flag (não reescreve) |
| END | `Validade = fParseData([Data de Validade])` (tipo *Data*) | datas texto → data; inválidas viram `null` |
| END | `NP_NS = [NP_Norm] & "\|" & [NS_Norm]` | chave NP+NS normalizada (não usar a coluna `NP NS` do SharePoint) |
| Cont_op | `V = fParseStatusManutencao([Status manutenção])`; `Venc_Final = [Vencimento da manutenção] ?? V[Venc]` | recupera vencimento que só está no texto |
| Eslinga | `ID_Norm = fNormalizaNP([ID_Eslinga])` | ID sem espaço/caixa; vazio = `null` |

## Decisões embutidas (revise)

1. **`fParseData` é estrita**: só `dd/mm/aaaa`. Datas com erro de digitação viram `null` e aparecem como “sem data” no painel, em vez de serem adivinhadas. Corrija na origem (relatório D).
2. **NP**: espaço interno simples é mantido; só aparas, NBSP e duplicados são removidos.
3. **NS**: sem padrão canônico definido. `fNSForaDoPadrao` usa `NS-nn` **provisoriamente**; veja `relatorios/extra_g_formatos_de_NS.csv` para decidir.
4. **Duplicados no END** (mesmo NP+NS): *não removidos aqui*. Regra sugerida para o painel (aguarda confirmação): considerar a maior `Validade` por `NP_NS`.
5. `Prev.:`/`Prazo:` em “Status manutenção” **não** são vencimento e ficam fora de `Venc`.

## Teste

`python fase0/scripts/test_normalizacao.py` valida as versões Python destas regras. **As funções M não puderam ser executadas neste ambiente** (sem Power Query); cole-as no Power BI Desktop e confira com os mesmos exemplos da tabela de testes do script.
