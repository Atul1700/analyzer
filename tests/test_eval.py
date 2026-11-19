"""Tests für eval.py. Kein Modellaufruf, kein Lebenslauf."""

import eval as ev


def zeile(meine, modell, dauer=1.0, fehler=""):
    return {"meine_passung": meine, "modell_passung": modell, "dauer_s": dauer, "fehler": fehler}


def test_kennzahlen_normalfall():
    k = ev.berechne_kennzahlen([zeile(6, 7), zeile(5, 8), zeile(4, 4), zeile(3, 7)])
    assert k["mittlere_abweichung"] == (1 + 3 + 0 + 4) / 4
    assert k["treffer_1"] == 2
    assert k["treffer_2"] == 2
    assert k["anzahl_fehler"] == 0
    assert k["gesamtdauer_s"] == 4.0


def test_kennzahlen_fehler_zaehlen_nicht_in_abweichung():
    k = ev.berechne_kennzahlen([zeile(6, 7), zeile(5, None, 2.5, "RuntimeError: x")])
    assert k["mittlere_abweichung"] == 1
    assert k["anzahl_bewertet"] == 1
    assert k["anzahl_fehler"] == 1
    assert k["gesamtdauer_s"] == 3.5


def test_kennzahlen_nur_fehler():
    k = ev.berechne_kennzahlen([zeile(6, None, 1.0, "x")])
    assert k["mittlere_abweichung"] is None
    assert k["treffer_1"] == 0


def test_kennzahlen_leer():
    assert ev.berechne_kennzahlen([])["anzahl_gesamt"] == 0


def test_modellname_fuer_datei():
    assert ev.modellname_fuer_datei("qwen3.5:4b") == "qwen3.5_4b"
    assert ev.modellname_fuer_datei("hf.co/user/model:Q4") == "hf.co_user_model_Q4"
