// Normaliza NP: troca NBSP/tab/quebra por espaço, colapsa espaços repetidos, apara as pontas e põe em MAIÚSCULAS.
// Espaço INTERNO simples é preservado (existem NPs legítimos como "MLTU S09").
// Espelho de norm_np() em fase0/scripts/extrair_e_auditar.py.
(t as nullable text) as nullable text =>
let
    a = if t = null then null else
        Text.Replace(Text.Replace(Text.Replace(Text.Replace(t, "#(00A0)", " "), "#(tab)", " "), "#(lf)", " "), "#(cr)", " "),
    partes = if a = null then {} else List.Select(Text.Split(a, " "), each _ <> ""),
    r = Text.Upper(Text.Combine(partes, " "))
in
    if r = "" then null else r
