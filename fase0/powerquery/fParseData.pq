// Converte texto dd/mm/aaaa (estrito, após trim) em date. Qualquer outro formato -> null (nunca adivinha).
// Ex.: "27/0/2024", "17/02/23", "08/042024", "06-07-2023" viram null e ficam visíveis como "sem data".
// Espelho de parse_data_txt().
(t as nullable text) as nullable date =>
let
    s = if t = null then null else Text.Trim(Text.Replace(t, "#(00A0)", " ")),
    formatoOk = s <> null and Text.Length(s) = 10 and Text.At(s, 2) = "/" and Text.At(s, 5) = "/",
    r = if formatoOk then try Date.FromText(s, [Format = "dd/MM/yyyy", Culture = "pt-BR"]) otherwise null else null
in
    r
