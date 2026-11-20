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


def test_bewerte_speichert_begruendung(tmp_path, monkeypatch):
    (tmp_path / "a.txt").write_text("Anzeige", encoding="utf-8")
    monkeypatch.setattr(ev.analyzer, "JOBS_DIR", tmp_path)

    class Fake:
        passung = 7
        begruendung = "Zeile eins\nZeile zwei"

    monkeypatch.setattr(ev.analyzer, "analysiere", lambda t, l: Fake())
    r = ev.bewerte({"datei": "a.txt", "meine_passung": 6}, "CV")
    assert r["begruendung"] == "Zeile eins Zeile zwei"
    assert r["abweichung"] == 1


def test_schreibe_ergebnis_hat_begruendung_spalte(tmp_path):
    import csv

    pfad = tmp_path / "out.csv"
    z = {k: None for k in ev.ERGEBNIS_SPALTEN}
    z.update(datei="a.txt", meine_passung=5, modell_passung=6, begruendung="Passt, weil X.")
    ev.schreibe_ergebnis(pfad, [z])
    zeilen = list(csv.DictReader(pfad.open(encoding="utf-8")))
    assert "begruendung" in zeilen[0]
    assert zeilen[0]["begruendung"] == "Passt, weil X."
