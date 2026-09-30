"""Casos de teste das regras de normalizacao (contrato para as versoes M)."""
import datetime as dt
from extrair_e_auditar import norm_np, parse_data_txt, parse_status_manutencao, classifica_data_txt

D = dt.date
assert norm_np("P7000115239 ") == "P7000115239"
assert norm_np("mltu\xa0s09") == "MLTU S09"
assert norm_np("MLTU   S09") == "MLTU S09"
assert norm_np("  ") is None and norm_np(None) is None
assert parse_data_txt("20/04/2011") == D(2011, 4, 20)
assert parse_data_txt("11/12/2022 ") == D(2022, 12, 11)          # espaco sobrando: corrigivel
for ruim in ("27/0/2024", "17/02/23", "08/042024", "06-07-2023", "008/03/2023", "31/02/2024", "", None):
    assert parse_data_txt(ruim) is None, ruim
assert classifica_data_txt("11/12/2022 ") == "ESPACO_SOBRANDO" and classifica_data_txt("17/02/23") == "INVALIDA"
assert parse_status_manutencao("Venc.: 26/12/2022 / END.: 01/03/2023") == (D(2022, 12, 26), D(2023, 3, 1))
assert parse_status_manutencao("Previsão de Venc.: 26/12/2022 / END.: 01/03/2023") == (D(2022, 12, 26), D(2023, 3, 1))
assert parse_status_manutencao("Venc.: 01/02/2023 / END:05/06/2023") == (D(2023, 2, 1), D(2023, 6, 5))
assert parse_status_manutencao("Prev.: 04/01/2022") == (None, None)
assert parse_status_manutencao("Prazo: 10/01/2022 a 20/01/2022") == (None, None)
assert parse_status_manutencao(None) == (None, None)
print("ok")
