// Limpeza de NS: apenas espaços/NBSP (NÃO muda caixa nem reescreve o formato).
// O formato canônico do NS ainda NÃO foi definido pela equipe (ver LEIA-ME). Use fNSForaDoPadrao para sinalizar.
(t as nullable text) as nullable text =>
let
    a = if t = null then null else
        Text.Replace(Text.Replace(Text.Replace(Text.Replace(t, "#(00A0)", " "), "#(tab)", " "), "#(lf)", " "), "#(cr)", " "),
    partes = if a = null then {} else List.Select(Text.Split(a, " "), each _ <> ""),
    r = Text.Combine(partes, " ")
in
    if r = "" then null else r
