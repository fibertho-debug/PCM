// TRUE quando o NS não segue o padrão PROVISÓRIO "NS-" + dígitos (ex.: NS-01).
// Só sinaliza; não corrige. Troque a regra aqui quando o padrão for definido.
(ns as nullable text) as logical =>
let
    s = fNormalizaNS(ns),
    resto = if s = null then "" else Text.AfterDelimiter(s, "NS-"),
    ok = s <> null and Text.StartsWith(s, "NS-") and resto <> ""
         and List.AllTrue(List.Transform(Text.ToList(resto), each _ >= "0" and _ <= "9"))
in
    not ok
