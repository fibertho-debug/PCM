// Extrai Vencimento e END do texto livre de "Status manutenção".
//   "Venc.: 26/12/2022 / END.: 01/03/2023"  -> [Venc = 26/12/2022, END = 01/03/2023]
//   "Previsão de Venc.: 26/12/2022"          -> [Venc = 26/12/2022, END = null]
//   "Prev.: 04/01/2022", "Prazo: ..."        -> null/null (é previsão de manutenção, NÃO vencimento)
// Requer fParseData. Espelho de parse_status_manutencao().
(t as nullable text) as record =>
let
    s = if t = null then "" else Text.Replace(t, "#(00A0)", " "),
    apos = (marcador as text) as nullable date =>
        let p = Text.PositionOf(s, marcador, Occurrence.First)   // sensível a maiúsculas: "END" não casa "pendente"
        in if p < 0 then null
           else fParseData(Text.Start(Text.Trim(Text.AfterDelimiter(Text.Middle(s, p), ":")), 10)),
    venc = apos("Venc"),
    fim  = apos("END")
in
    [Venc = venc, END = fim]
