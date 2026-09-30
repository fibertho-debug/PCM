# Fase 0 - resumo da auditoria

Gerado em 2026-09-30. Fonte: copias dentro das planilhas (nao o SharePoint ao vivo).

| Rel. | Metrica | Obtido | Spec sec. 8 | Confere? |
|---|---|---:|---:|---|
| a | chaves duplicadas | 220 | 220 | sim |
| a | linhas nessas chaves | 757 | 757 | sim |
| a | chaves com NP diferente | 201 | 201 | sim |
| a | linhas sem chave (vazias, ignoradas) | 254 |  |  |
| b | linhas do catalogo | 246 | 246 | sim |
| b | NPs unicos (normalizados) | 242 |  |  |
| b | linhas sem peso | 166 | 173 | **NAO** |
| b | NPs unicos sem peso | 163 |  |  |
| b | linhas com peso em texto | 4 |  |  |
| b | linhas com NP repetido no catalogo | 8 |  |  |
| b | linhas sem alguma dimensao | 206 |  |  |
| c | NPs unicos no PCM real | 117 | 117 | sim |
| c | NPs do PCM real ausentes do catalogo | 8 | 8 | sim |
| c | NPs do PCM real com NP nulo (itens) | 2 |  |  |
| d | linhas na lista END | 4819 | 4819 | sim |
| d | datas em texto | 4819 | 4819 | sim |
| d |   das quais invalidas (nao viram data) | 15 |  |  |
| d |   com espaco sobrando (corrigivel) | 3 |  |  |
| d | linhas repetidas alem da 1a (NP NS) | 1455 | 1455 | sim |
| d | linhas envolvidas em NP NS repetido | 2217 |  |  |
| d | linhas repetidas por NP+NS normalizado | 1603 |  |  |
| f | classes em uso fora do cadastro (catalogo) | 4 | 4 | sim |
| f | codigos de operacao em Cont_op fora de Dados!M | 43 |  |  |
| f | itens do PCM real com classe fora do cadastro | 32 | 31 | **NAO** |
| f | itens do PCM real com classe = #REF! (erro de formula) | 1 |  |  |
| f | itens do PCM real (linhas com item ou NP) | 130 | 127 | **NAO** |
