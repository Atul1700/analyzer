"""Tests für analyzer.py. Kein Modellaufruf, kein echter Lebenslauf."""

import pytest
from pydantic import ValidationError

import analyzer
from analyzer import JobAnalyse


def mache_analyse(**ueberschreiben) -> JobAnalyse:
    """Hilfsfunktion: gültige Beispiel-Analyse, einzelne Felder überschreibbar."""
    daten = dict(
        jobtitel="Entwickler",
        firma=None,
        muss_skills=[],
        nice_to_have=[],
        remote_moeglich=None,
        seniority=None,
        erfuellt=[],
        fehlt=[],
        passung=5,
        begruendung="Test",
    )
    daten.update(ueberschreiben)
    return JobAnalyse(**daten)


# --- lade_anzeigen ---

def test_lade_anzeigen_liest_und_sortiert(tmp_path, monkeypatch):
    (tmp_path / "b.txt").write_text("Anzeige B", encoding="utf-8")
    (tmp_path / "a.txt").write_text("Anzeige A", encoding="utf-8")
    (tmp_path / "ignoriert.md").write_text("kein txt", encoding="utf-8")
    # monkeypatch ersetzt JOBS_DIR nur für diesen Test
    monkeypatch.setattr(analyzer, "JOBS_DIR", tmp_path)
    assert analyzer.lade_anzeigen() == [("a.txt", "Anzeige A"), ("b.txt", "Anzeige B")]


def test_lade_anzeigen_fehlender_ordner(tmp_path, monkeypatch):
    monkeypatch.setattr(analyzer, "JOBS_DIR", tmp_path / "gibt_es_nicht")
    with pytest.raises(SystemExit, match="nicht gefunden"):
        analyzer.lade_anzeigen()


# --- lade_lebenslauf ---

def test_lade_lebenslauf_liest_datei(tmp_path, monkeypatch):
    datei = tmp_path / "cv.txt"
    datei.write_text("Mein Lebenslauf", encoding="utf-8")
    monkeypatch.setattr(analyzer, "LEBENSLAUF_DATEI", datei)
    assert analyzer.lade_lebenslauf() == "Mein Lebenslauf"


def test_lade_lebenslauf_fehlende_datei(tmp_path, monkeypatch):
    monkeypatch.setattr(analyzer, "LEBENSLAUF_DATEI", tmp_path / "fehlt.txt")
    with pytest.raises(SystemExit, match="nicht gefunden"):
        analyzer.lade_lebenslauf()


# --- _json_extrahieren ---

def test_json_extrahieren_aus_codeblock():
    roh = 'Hier das Ergebnis:\n```json\n{"a": 1}\n```\nFertig.'
    assert analyzer._json_extrahieren(roh) == '{"a": 1}'


def test_json_extrahieren_ohne_codeblock():
    assert analyzer._json_extrahieren('  {"a": 1}  ') == '{"a": 1}'


# --- JobAnalyse ---

def test_passung_11_wird_abgelehnt():
    with pytest.raises(ValidationError):
        mache_analyse(passung=11)


def test_passung_6_wird_akzeptiert():
    assert mache_analyse(passung=6).passung == 6


# --- baue_prompt ---

def test_baue_prompt_enthaelt_anzeige_und_lebenslauf():
    prompt = analyzer.baue_prompt("ANZEIGE-XYZ", "LEBENSLAUF-ABC")
    assert "ANZEIGE-XYZ" in prompt
    assert "LEBENSLAUF-ABC" in prompt


def test_baue_prompt_enthaelt_skala_anker():
    prompt = analyzer.baue_prompt("A", "L")
    for anker in ["0-1:", "2-3:", "4-5:", "6-7:", "8-9:", "10:", "Seniority", "Grundkenntnisse"]:
        assert anker in prompt


# --- top_skills ---

def test_top_skills_zaehlt_richtig():
    analysen = [
        mache_analyse(muss_skills=["Python", "SQL"]),
        mache_analyse(muss_skills=["Python", "Docker"]),
        mache_analyse(muss_skills=["Python", "SQL"]),
    ]
    assert analyzer.top_skills(analysen) == [("Python", 3), ("SQL", 2), ("Docker", 1)]


def test_top_skills_begrenzt_auf_n():
    analysen = [mache_analyse(muss_skills=["A", "B", "C"])]
    assert len(analyzer.top_skills(analysen, n=2)) == 2
