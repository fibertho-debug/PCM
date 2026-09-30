#!/usr/bin/env python3
"""Fase 0 - auditoria de dados do PCM (somente leitura).

Le COPIAS das planilhas (abertas em modo read-only; nenhum arquivo e alterado)
e gera os relatorios CSV para os donos corrigirem na origem (secao 8 da spec).

Uso:
  python extrair_e_auditar.py --padrao "PCM Padrao Sonda.xlsm" \
      --pcm "PCM - ITH BUZ-118D NS-61 Rev.0.xlsm" --saida ../relatorios

Limite importante: as abas `Operacoes`, `END` e `Eslinga` sao COPIAS das listas do
SharePoint no momento em que a planilha foi salva. Os numeros refletem aquela data.
"""
import argparse
import datetime as dt
import re
import warnings
from collections import Counter
from pathlib import Path

import openpyxl
import pandas as pd

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------- normalizacao
# (espelhadas em fase0/powerquery/*.pq - mantenha as duas versoes iguais)
RE_DATA = re.compile(r"^\d{2}/\d{2}/\d{4}$")


def limpa(x):
    """Converte para texto, troca NBSP/tab/quebra por espaco e colapsa espacos."""
    if x is None or (isinstance(x, float) and x != x):
        return None
    s = re.sub(r"\s+", " ", str(x)).strip()
    return s or None


def norm_np(x):
    s = limpa(x)
    return s.upper() if s else None


def compacto(x):
    s = norm_np(x)
    return s.replace(" ", "") if s else None


def parse_data_txt(x):
    """dd/mm/aaaa estrito (depois de trim). Qualquer outra coisa -> None."""
    s = limpa(x)
    if not s or not RE_DATA.match(s):
        return None
    try:
        return dt.datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        return None


def classifica_data_txt(x):
    if x is None or (isinstance(x, float) and x != x) or str(x).strip() == "":
        return "VAZIA"
    if parse_data_txt(x) is None:
        return "INVALIDA"
    return "ESPACO_SOBRANDO" if str(x) != str(x).strip() else "OK_TEXTO"


RE_VENC = re.compile(r"Venc[^:]*:\s*(\d{2}/\d{2}/\d{4})")
RE_END = re.compile(r"END\.?\s*:\s*(\d{2}/\d{2}/\d{4})")


def parse_status_manutencao(x):
    """Extrai (venc, end) de textos como 'Venc.: 26/12/2022 / END.: 01/03/2023'.
    'Prev.:', 'Prazo:' etc. sao previsao de manutencao e NAO sao vencimento."""
    s = limpa(x) or ""
    m1, m2 = RE_VENC.search(s), RE_END.search(s)
    return (parse_data_txt(m1.group(1)) if m1 else None,
            parse_data_txt(m2.group(1)) if m2 else None)


def padrao_ns(x):
    """Mascara o NS: digitos->9, letras->A (para ver os formatos em uso)."""
    s = limpa(x)
    if not s:
        return None
    return re.sub(r"[A-Za-z]+", "A", re.sub(r"\d+", "9", s))


# ------------------------------------------------------------------- leitura
def le_aba(wb, nome):
    rows = list(wb[nome].iter_rows(values_only=True))
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df.insert(0, "linha_planilha", range(2, len(df) + 2))
    return df


def le_itens_pcm(wb, aba, fonte):
    """Itens de uma aba de PCM; localiza colunas pelo cabecalho (layouts diferem)."""
    rows = list(wb[aba].iter_rows(values_only=True))
    h = next(i for i, r in enumerate(rows)
             if any(isinstance(c, str) and c.strip() == "NP" for c in r))
    hdr = [re.sub(r"\s+", " ", str(c)).strip() if c else "" for c in rows[h]]
    col = lambda nome: hdr.index(nome)
    c_item, c_np = col("Item"), col("NP")
    c_cls = next(i for i, c in enumerate(hdr) if c.startswith("Classe"))
    c_desc = next(i for i, c in enumerate(hdr) if c.startswith("Descri"))
    out = []
    for n, r in enumerate(rows[h + 1:], start=h + 2):
        if r[c_item] is None and r[c_np] is None:
            continue
        out.append(dict(fonte=fonte, linha_planilha=n, item=r[c_item], np_bruto=r[c_np],
                        classe=r[c_cls], descricao=r[c_desc]))
    return pd.DataFrame(out)


def le_catalogo_e_cadastros(wb):
    rows = list(wb["Dados"].iter_rows(values_only=True))
    cat = pd.DataFrame(
        [(n,) + tuple(r[:7]) for n, r in enumerate(rows[1:], start=2) if r[0] is not None],
        columns=["linha_planilha", "NP", "Descricao", "Classe", "Comprimento", "Largura", "Altura", "Peso"])
    get = lambda idx: [r[idx] for r in rows[1:] if idx < len(r) and r[idx] is not None]
    cad = {"Frente": get(8), "TAG": get(10), "Operacao": get(12), "Unidade": get(14),
           "Classe": get(16), "StatusRT": get(18), "Etapa": get(20)}
    return cat, cad


def salva(df, caminho, cabecalho):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
        for linha in cabecalho:
            f.write("# " + linha + "\n")  # comentario: apague as linhas '#' antes de importar
        df.to_csv(f, sep=";", index=False, lineterminator="\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--padrao", required=True)
    ap.add_argument("--pcm", required=True)
    ap.add_argument("--saida", default="../relatorios")
    a = ap.parse_args()
    saida = Path(a.saida)
    hoje = dt.date.today().isoformat()
    cab = lambda t: [f"{t}", f"Gerado em {hoje} a partir de copias nas planilhas (nao do SharePoint ao vivo).",
                     "Separador ';' - codificacao UTF-8. Linhas iniciadas com '#' sao comentario."]

    wb = openpyxl.load_workbook(a.padrao, read_only=True, data_only=True)
    wp = openpyxl.load_workbook(a.pcm, read_only=True, data_only=True)
    op, end, esl = le_aba(wb, "Operações"), le_aba(wb, "END"), le_aba(wb, "Eslinga")
    cat, cad = le_catalogo_e_cadastros(wb)
    itens = pd.concat([le_itens_pcm(wp, "ITH", "PCM real (ITH BUZ-118D NS-61 Rev.0)"),
                       le_itens_pcm(wb, "ITH", "Padrao Sonda (aba ITH)")], ignore_index=True)
    itens["np"] = itens.np_bruto.map(norm_np)
    cat["np"] = cat.NP.map(norm_np)
    cat["np_compacto"] = cat.NP.map(compacto)
    resumo = []  # (relatorio, metrica, obtido, spec)

    # ---- a) Cont_op: chave Poco+Fase+PIOS duplicada -------------------------
    K = "Poço + Fase + PIOS"
    d = op[op[K].notna()].copy()
    d["np_norm"] = d["NP"].map(norm_np)
    g = d.groupby(K)
    d["linhas_na_chave"] = g[K].transform("size")
    d["nps_distintos_na_chave"] = g["np_norm"].transform("nunique")
    ra = d[d.linhas_na_chave > 1].sort_values([K, "linha_planilha"])
    ra = ra.assign(np_difere=ra.nps_distintos_na_chave > 1)
    cols = ["linha_planilha", K, "linhas_na_chave", "nps_distintos_na_chave", "np_difere", "ID", "NP", "NS",
            "NP + NS", "Fase", "TAG", "Sonda / Barco", "Poço", "DESCRIÇÃO", "Status Processo", "Status PCM",
            "Responsável DISP"]
    salva(ra[cols], saida / "a_cont_op_chaves_duplicadas.csv",
          cab("A) Cont_op: chaves Poco+Fase+PIOS repetidas") +
          ["Acao: dono do Cont_op decide qual linha vale. Nunca usar esta chave como identificador."])
    n_chaves = ra[K].nunique()
    n_dif = ra[ra.np_difere][K].nunique()
    resumo += [("a", "chaves duplicadas", n_chaves, 220), ("a", "linhas nessas chaves", len(ra), 757),
               ("a", "chaves com NP diferente", n_dif, 201),
               ("a", "linhas sem chave (vazias, ignoradas)", int(op[K].isna().sum()), None)]

    # ---- b) catalogo sem peso / dimensoes -----------------------------------
    uso_cont = d["np_norm"].value_counts()
    uso_pcm = itens[itens.fonte.str.startswith("PCM real")].np.value_counts()
    cat["sem_peso"] = cat.Peso.isna()
    cat["peso_em_texto"] = cat.Peso.map(lambda v: isinstance(v, str))
    for c in ("Comprimento", "Largura", "Altura"):
        cat["sem_" + c.lower()] = cat[c].isna()
    cat["np_repetido_no_catalogo"] = cat.np.duplicated(keep=False)
    cat["np_com_espaco_ou_minuscula"] = cat.NP.map(lambda v: isinstance(v, str) and v != norm_np(v))
    cat["linhas_cont_op"] = cat.np.map(uso_cont).fillna(0).astype(int)
    cat["itens_no_pcm_real"] = cat.np.map(uso_pcm).fillna(0).astype(int)
    prob = cat[cat.sem_peso | cat.peso_em_texto | cat.sem_comprimento | cat.sem_largura | cat.sem_altura]
    prob = prob.sort_values(["itens_no_pcm_real", "linhas_cont_op"], ascending=False)
    cols = ["linha_planilha", "NP", "Descricao", "Classe", "sem_peso", "peso_em_texto", "sem_comprimento",
            "sem_largura", "sem_altura", "np_repetido_no_catalogo", "np_com_espaco_ou_minuscula",
            "itens_no_pcm_real", "linhas_cont_op"]
    salva(prob[cols], saida / "b_catalogo_sem_peso_dimensoes.csv",
          cab("B) Catalogo (aba Dados A-G): NPs sem peso e/ou dimensoes") +
          ["Ordenado por uso (PCM real, depois Cont_op): comece pelos NPs mais usados."])
    resumo += [("b", "linhas do catalogo", len(cat), 246), ("b", "NPs unicos (normalizados)", cat.np.nunique(), None),
               ("b", "linhas sem peso", int(cat.sem_peso.sum()), 173),
               ("b", "NPs unicos sem peso", int(cat[cat.sem_peso].np.nunique()), None),
               ("b", "linhas com peso em texto", int(cat.peso_em_texto.sum()), None),
               ("b", "linhas com NP repetido no catalogo", int(cat.np_repetido_no_catalogo.sum()), None),
               ("b", "linhas sem alguma dimensao", int((cat.sem_comprimento | cat.sem_largura | cat.sem_altura).sum()), None)]

    # ---- c) NPs usados nos PCMs e ausentes do catalogo ----------------------
    cat_set, cat_comp = set(cat.np), set(cat.np_compacto)
    it = itens[itens.np.notna()].copy()
    it["status"] = it.np.map(lambda n: "NO_CATALOGO" if n in cat_set else (
        "SO_SEM_ESPACOS" if n.replace(" ", "") in cat_comp else "AUSENTE"))
    it["np_bruto_diferente"] = it.np_bruto.map(lambda v: isinstance(v, str) and v != norm_np(v))
    rc = (it[it.status != "NO_CATALOGO"].groupby(["fonte", "np", "status"])
          .agg(np_bruto=("np_bruto", "first"), np_com_espaco_ou_minuscula=("np_bruto_diferente", "max"),
               qtd_itens=("item", "size"), itens=("item", lambda s: ", ".join(map(str, s))),
               descricao=("descricao", "first"), classe=("classe", "first")).reset_index())
    salva(rc, saida / "c_np_usados_ausentes_do_catalogo.csv",
          cab("C) NPs usados em PCMs e ausentes do catalogo") +
          ["AUSENTE: cadastrar no catalogo. SO_SEM_ESPACOS: existe no catalogo com grafia diferente (espaco)."])
    real = it[it.fonte.str.startswith("PCM real")]
    resumo += [("c", "NPs unicos no PCM real", real.np.nunique(), 117),
               ("c", "NPs do PCM real ausentes do catalogo", real[real.status != "NO_CATALOGO"].np.nunique(), 8),
               ("c", "NPs do PCM real com NP nulo (itens)", int(itens[itens.fonte.str.startswith('PCM real')].np.isna().sum()), None)]

    # ---- d) END: NP+NS repetido e datas em texto ----------------------------
    e = end.copy()
    e["data_estado"] = e["Data de Validade"].map(classifica_data_txt)
    e["data_iso"] = pd.to_datetime(e["Data de Validade"].map(parse_data_txt))
    e["np_ns_norm"] = e["NP"].map(norm_np).fillna("") + "|" + e["NS"].map(limpa).fillna("")
    e["linhas_no_grupo"] = e.groupby("NP NS")["NP NS"].transform("size")
    e["datas_distintas_no_grupo"] = e.groupby("NP NS")["data_iso"].transform("nunique")
    e["linhas_no_grupo_normalizado"] = e.groupby("np_ns_norm")["np_ns_norm"].transform("size")
    mx = e.groupby("NP NS")["data_iso"].transform("max")
    e["sugestao_manter"] = (e.data_iso == mx) & e.data_iso.notna() & (e.linhas_no_grupo > 1)
    rep = e[(e.linhas_no_grupo > 1) | (e.data_estado.isin(["INVALIDA", "ESPACO_SOBRANDO", "VAZIA"]))]
    rep = rep.assign(motivo=rep.apply(lambda r: "+".join(
        ([f"NP_NS_REPETIDO"] if r.linhas_no_grupo > 1 else []) +
        ([f"DATA_{r.data_estado}"] if r.data_estado != "OK_TEXTO" else [])), axis=1))
    rep = rep.sort_values(["NP NS", "linha_planilha"])
    cols = ["linha_planilha", "ID", "NP", "NS", "NP NS", "motivo", "linhas_no_grupo", "datas_distintas_no_grupo",
            "Data de Validade", "data_estado", "data_iso", "sugestao_manter", "Ordem", "Nº Sequencial",
            "Title", "Criado por"]
    salva(rep[cols], saida / "d_end_np_ns_repetido_e_datas_texto.csv",
          cab("D) Lista END: NP+NS repetido e datas em texto") +
          ["TODAS as 4.819 datas estao como texto (dd/mm/aaaa); aqui so as linhas com problema alem disso.",
           "'sugestao_manter' = data de validade mais recente do grupo. E SUGESTAO: repetidos podem ser recertificacoes validas."])
    resumo += [("d", "linhas na lista END", len(e), 4819), ("d", "datas em texto", len(e), 4819),
               ("d", "  das quais invalidas (nao viram data)", int((e.data_estado == "INVALIDA").sum()), None),
               ("d", "  com espaco sobrando (corrigivel)", int((e.data_estado == "ESPACO_SOBRANDO").sum()), None),
               ("d", "linhas repetidas alem da 1a (NP NS)", int(e["NP NS"].duplicated().sum()), 1455),
               ("d", "linhas envolvidas em NP NS repetido", int((e.linhas_no_grupo > 1).sum()), None),
               ("d", "linhas repetidas por NP+NS normalizado", int(e.np_ns_norm.duplicated().sum()), None)]

    # ---- e) Eslingas ---------------------------------------------------------
    s = esl.copy()
    s["id_norm"] = s["ID_Eslinga"].map(lambda v: (limpa(v) or "").upper() or None)
    s["linhas_com_mesmo_id"] = s.groupby("id_norm")["id_norm"].transform("size")
    s["certificados_distintos_no_id"] = s.groupby("id_norm")["Eslinga"].transform("nunique")
    flags = {
        "ID_DUPLICADO": s.id_norm.notna() & (s.linhas_com_mesmo_id > 1),
        "SEM_ID": s.id_norm.isna(),
        "EQUI_N_IDENTIFICADO": s["Status_eslinga"].astype(str).str.contains("n_identificado", case=False),
        "SEM_VALIDADE": s["Validade(M/D/A)"].isna()}
    s["motivo"] = pd.concat([m.map({True: k, False: ""}) for k, m in flags.items()], axis=1).apply(
        lambda r: "+".join(x for x in r if x), axis=1)
    re_ = s[s.motivo != ""].sort_values(["id_norm", "linha_planilha"], na_position="last")
    cols = ["linha_planilha", "ID_Eslinga", "motivo", "linhas_com_mesmo_id", "certificados_distintos_no_id",
            "Eslinga", "ID_BR", "Validade(M/D/A)", "Status_eslinga", "Localização", "Capacidade(T)",
            "Comprimento(m)", "Pernas", "Cliente", "NP"]
    salva(re_[cols], saida / "e_eslingas_id_duplicado_ou_nao_identificado.csv",
          cab("E) Eslingas: ID duplicado, sem ID, 'Equi_n_identificado' ou sem validade") +
          ["ID repetido com certificados diferentes pode ser recertificacao: confirmar antes de apagar."])
    bruto_dup = int(s["ID_Eslinga"].astype(str).duplicated().sum())
    resumo += [("e", "linhas na lista", len(s), None),
               ("e", "IDs repetidos alem do 1o (contagem bruta, inclui vazios)", bruto_dup, 262),
               ("e", "  dos quais: IDs nao vazios repetidos", int((flags['ID_DUPLICADO'] & s.id_norm.duplicated()).sum()), None),
               ("e", "  dos quais: linhas sem ID", int(flags["SEM_ID"].sum()), None),
               ("e", "Equi_n_identificado", int(flags["EQUI_N_IDENTIFICADO"].sum()), 37),
               ("e", "sem validade", int(flags["SEM_VALIDADE"].sum()), None)]

    # ---- f) classes e operacoes fora dos cadastros --------------------------
    linhas = []
    cls_ok = {norm_np(c) for c in cad["Classe"] if not str(c).lower().startswith("http")}
    for c in cad["Classe"]:
        if str(c).lower().startswith(("http", "www")):
            linhas.append(dict(tipo="LIXO_NO_CADASTRO", cadastro="Classe", valor=c, ocorrencias=1, no_cadastro="",
                               onde="Dados!Q (lista de classes)", observacao="URL de tutorial dentro da lista"))
    for fonte, serie in (("Catalogo (Dados!C)", cat.Classe), ("PCM real", itens[itens.fonte.str.startswith("PCM real")].classe)):
        for v, n in Counter(norm_np(x) for x in serie if limpa(x)).items():
            linhas.append(dict(tipo="CLASSE_EM_USO", cadastro="Classe", valor=v, ocorrencias=n,
                               no_cadastro="sim" if v in {c.upper() for c in cls_ok if c} else "NAO",
                               onde=fonte, observacao=""))
    frentes_lixo = [f for f in cad["Frente"] if isinstance(f, str) and len(f) > 14]
    for f in cad["Frente"]:
        if f in frentes_lixo:
            linhas.append(dict(tipo="LIXO_NO_CADASTRO", cadastro="Frente", valor=f, ocorrencias=1, no_cadastro="",
                               onde="Dados!I (lista de frentes)", observacao="observacao solta dentro da lista"))
    ops_dados = [norm_np(o) for o in cad["Operacao"]]
    for o, n in Counter(ops_dados).items():
        if n > 1:
            linhas.append(dict(tipo="DUPLICADO_NO_CADASTRO", cadastro="Operacao", valor=o, ocorrencias=n,
                               no_cadastro="sim", onde="Dados!M", observacao="valor repetido na lista"))
    fases = op["Fase"].map(norm_np).value_counts()
    for v, n in fases.items():
        livre = len(v) > 10 or " " in v or v in {"N/A", "TODAS", "TODAS AS FASES"}
        linhas.append(dict(tipo="OPERACAO_EM_USO", cadastro="Operacao", valor=v, ocorrencias=int(n),
                           no_cadastro="sim" if v in set(ops_dados) else "NAO", onde="Cont_op!Fase",
                           observacao="texto livre / nao e codigo de operacao" if livre else ""))
    for o in sorted(set(ops_dados) - set(fases.index)):
        linhas.append(dict(tipo="OPERACAO_SO_NO_CADASTRO", cadastro="Operacao", valor=o, ocorrencias=0,
                           no_cadastro="sim", onde="Dados!M", observacao="nao aparece em Cont_op!Fase"))
    rf = pd.DataFrame(linhas)
    salva(rf, saida / "f_classes_e_operacoes_fora_dos_cadastros.csv",
          cab("F) Classes e operacoes em uso fora dos cadastros + lixo dentro das listas") +
          ["Operacao em uso = Cont_op!Fase (campo de texto livre). Decidir: ampliar cadastro ou padronizar o campo."])
    cls_fora = rf[(rf.tipo == "CLASSE_EM_USO") & (rf.no_cadastro == "NAO")]
    cls_pcm = rf[(rf.tipo == "CLASSE_EM_USO") & (rf.onde == "PCM real")]
    ops_fora = rf[(rf.tipo == "OPERACAO_EM_USO") & (rf.no_cadastro == "NAO") & (rf.observacao == "")]
    resumo += [("f", "classes em uso fora do cadastro (catalogo)", cls_fora[cls_fora.onde.str.startswith("Catalogo")].valor.nunique(), 4),
               ("f", "codigos de operacao em Cont_op fora de Dados!M", ops_fora.valor.nunique(), None),
               ("f", "itens do PCM real com classe fora do cadastro", int(cls_pcm[(cls_pcm.no_cadastro == "NAO") & (cls_pcm.valor != "#REF!")].ocorrencias.sum()), 31),
               ("f", "itens do PCM real com classe = #REF! (erro de formula)", int(cls_pcm[cls_pcm.valor == "#REF!"].ocorrencias.sum()), None),
               ("f", "itens do PCM real (linhas com item ou NP)", int((itens.fonte.str.startswith("PCM real")).sum()), 127)]

    # ---- extra: formatos de NS em uso (subsidio p/ definir o padrao) ---------
    ns = pd.concat([op.NS.map(padrao_ns).rename("padrao").to_frame().assign(lista="Cont_op"),
                    end.NS.map(padrao_ns).rename("padrao").to_frame().assign(lista="END")])
    ex = {}
    for nome, col in (("Cont_op", op.NS), ("END", end.NS)):
        for v in col.dropna():
            ex.setdefault((nome, padrao_ns(v)), []).append(limpa(v))
    g = ns.dropna().groupby(["lista", "padrao"]).size().reset_index(name="linhas")
    g["exemplos"] = g.apply(lambda r: " | ".join(list(dict.fromkeys(ex[(r.lista, r.padrao)]))[:4]), axis=1)
    g = g.sort_values(["lista", "linhas"], ascending=[True, False])
    salva(g, saida / "extra_g_formatos_de_NS.csv",
          cab("EXTRA) Formatos de NS em uso (9=digitos, A=letras). Base para definir o padrao canonico."))

    # ---- resumo --------------------------------------------------------------
    md = ["# Fase 0 - resumo da auditoria", "",
          f"Gerado em {hoje}. Fonte: copias dentro das planilhas (nao o SharePoint ao vivo).", "",
          "| Rel. | Metrica | Obtido | Spec sec. 8 | Confere? |", "|---|---|---:|---:|---|"]
    for r, m, o, sp in resumo:
        ok = "" if sp is None else ("sim" if o == sp else "**NAO**")
        md.append(f"| {r} | {m} | {o} | {'' if sp is None else sp} | {ok} |")
    (saida / "RESUMO.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
