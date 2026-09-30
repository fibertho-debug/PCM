# Fase 0 — limpeza de dados

Base: seção 8 de `ESPECIFICACAO_PCM.md`. Tudo foi gerado a partir de **cópias** das planilhas (originais intocados) por `scripts/extrair_e_auditar.py`. Os CSVs ficam em `relatorios/` (fora do git). `relatorios/RESUMO.md` traz as contagens.

**Ressalva:** as abas `Operações` (Cont_op), `END` e `Eslinga` são cópias do SharePoint no dia em que a planilha foi salva. Os donos devem corrigir **na origem** e reexecutar o script com uma exportação nova.

| Relatório | Dono sugerido | O que pedir |
|---|---|---|
| a_cont_op_chaves_duplicadas | dono do Cont_op (PS) | definir qual linha vale; 201 das 220 chaves têm NP diferente, ou seja, a chave Poço+Fase+PIOS não identifica o item |
| b_catalogo_sem_peso_dimensoes | dono do catálogo | preencher, começando pelos NPs mais usados (colunas `itens_no_pcm_real`, `linhas_cont_op`) |
| c_np_usados_ausentes_do_catalogo | dono do catálogo | cadastrar os 8 NPs ausentes; ver observações abaixo |
| d_end_np_ns_repetido_e_datas_texto | Qualidade (SAMSS) | converter a coluna para tipo Data; corrigir 15 datas inválidas e 3 com espaço |
| e_eslingas_id_duplicado_ou_nao_identificado | Planning Subsea | resolver IDs duplicados, vazios e “Equi_n_identificado” |
| f_classes_e_operacoes_fora_dos_cadastros | Programadores | ampliar cadastros ou padronizar; limpar lixo das listas |
| extra_g_formatos_de_NS | Programadores / PS | escolher o formato canônico do NS |

## Onde o resultado NÃO bate com a seção 8 (verificar antes de confiar em qualquer um dos lados)

- **Catálogo sem peso: 166 linhas (163 NPs únicos), a spec diz 173.** Não consegui reproduzir 173 com nenhum critério razoável (nulo, texto, zero). Possível causa: o catálogo mudou depois da contagem. Não ajustei o critério para “bater”.
- **Itens do PCM real: 130 linhas com item/NP, a spec diz 127; classes fora do cadastro: 32, a spec diz 31.** Diferença pequena, provavelmente linhas de rodapé/estoque contadas ou não. Sem impacto nas ações.
- **Operações “só no Dados” (spec): ITCAP, RTCAP e HWO.** Nesta cópia do Cont_op, **ITCAP (24 linhas) e RTCAP (19) existem**; só HWO está ausente. IMCV, RTH e RMCV só no Cont_op: confere.
- Eslingas: os 262 “IDs duplicados” da spec só reproduzem na contagem bruta, que **inclui os vazios**. Após normalizar (trim/caixa), são 191 repetições de IDs preenchidos **mais** 76 linhas sem ID; o relatório separa por `motivo`.

## Achados que a spec não cita

1. **Catálogo com NP repetido (8 linhas, 4 NPs)**, alguns com descrições diferentes (ex.: `P7000099748`, `P7000106402`). O catálogo precisa de chave única.
2. **Campo “Fase” do Cont_op é texto livre** (82 valores distintos, muitos são descrição de serviço, “TODAS AS FASES”, “N/A”). Não é uma lista de operações; o cadastro não cobre isso ampliando a lista.
3. **Classe `#REF!`** (erro de fórmula) no item 57 do PCM real.
4. **Células de NP com mais de um NP** (`500103829 / 500006166`) ou NP incompleto (`MLTU`) no PCM real.
5. **Vencimento de manutenção só no texto:** 1.721 linhas do Cont_op têm a coluna de vencimento vazia; em 274 há `Venc.: dd/mm/aaaa` em “Status manutenção”. `Prev.:` e `Prazo:` são previsão de manutenção, não vencimento: ficam fora.
6. **Colunas de dias calculadas e gravadas com `HOJE` congelado** (ex.: “Dias restantes” = −627 com HOJE em 31/07/2023). O painel **não deve usar essas colunas**; recalcula contra HOJE.
7. **254 linhas vazias no fim do Cont_op** (sem chave); ignoradas.
8. Se os repetidos do END forem recertificações legítimas (várias datas por NP+NS), a “limpeza” correta é escolher a vigente, não apagar. O relatório D marca a mais recente como `sugestao_manter`; é sugestão, não aplicada.
9. Os textos do cadastro de Frente, Classe e Operação continuam dentro de listas de validação no Excel; o lixo está listado em F.

## Passos de Power Query

Em `powerquery/` (um `.pq` por regra) e `powerquery/PASSOS_POWER_QUERY.md`. As versões Python (`scripts/test_normalizacao.py`) passam nos testes; **as funções M não foram executadas** (sem Power Query aqui).

## Fora do escopo desta entrega
TAGs fora do dropdown (spec: 3 de 24) e derivação do status do item (coluna B) — não implementados.
