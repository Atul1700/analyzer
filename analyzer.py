"""
Job-Anzeigen-Analyzer
---------------------
Liest Stellenanzeigen (Textdateien in data/jobs/), lässt ein LLM die
Anforderungen als strukturiertes JSON extrahieren und zählt am Ende,
welche Skills am häufigsten verlangt werden.

Lernziele: Python-Grundlagen, lokales LLM (Ollama), strukturierte Ausgabe mit Pydantic.
Die Stellen mit "TODO" füllst DU aus.
"""

import json
from collections import Counter
from pathlib import Path

from pydantic import BaseModel

import llm

JOBS_DIR = Path("data/jobs")
LEBENSLAUF_DATEI = Path("data/lebenslauf.txt")


class JobAnalyse(BaseModel):
    """Das Schema, das das LLM zurückgeben soll."""
    jobtitel: str
    firma: str | None
    muss_skills: list[str]
    nice_to_have: list[str]
    remote_moeglich: bool | None
    seniority: str | None  # z. B. "Junior", "Mid", "Senior"


def lade_anzeigen() -> list[tuple[str, str]]:
    """Gibt eine sortierte Liste von (dateiname, text) für alle .txt-Dateien in data/jobs/ zurück."""
    if not JOBS_DIR.is_dir():
        raise SystemExit(f"Ordner '{JOBS_DIR}' nicht gefunden. Lege ihn an und füge .txt-Anzeigen hinzu.")
    dateien = sorted(JOBS_DIR.glob("*.txt"))
    if not dateien:
        raise SystemExit(f"Keine Anzeigen in '{JOBS_DIR}' gefunden. Lege dort mindestens eine .txt-Datei ab.")
    return [(datei.name, datei.read_text(encoding="utf-8")) for datei in dateien]


def lade_lebenslauf() -> str:
    """Liest data/lebenslauf.txt (liegt nur lokal, steht in .gitignore)."""
    if not LEBENSLAUF_DATEI.is_file():
        raise SystemExit(
            f"Datei '{LEBENSLAUF_DATEI}' nicht gefunden. "
            "Kopiere data/lebenslauf_beispiel.txt nach data/lebenslauf.txt und trage deine Daten ein."
        )
    return LEBENSLAUF_DATEI.read_text(encoding="utf-8")


def baue_prompt(anzeigentext: str) -> str:
    """Erstellt den Prompt für das LLM."""
    # TODO 2: Schreibe einen klaren Prompt. Er soll:
    #   - die Aufgabe erklären (Anforderungen extrahieren)
    #   - NUR JSON nach dem Schema von JobAnalyse verlangen
    #   - Skills normalisieren (z. B. "Python 3" -> "Python")
    #   - den Anzeigentext enthalten
    raise NotImplementedError


def analysiere(anzeigentext: str) -> JobAnalyse:
    """Schickt eine Anzeige ans LLM und gibt das validierte Ergebnis zurück."""
    rohtext = llm.frage_modell(baue_prompt(anzeigentext))
    # TODO 3: rohtext als JSON parsen und mit JobAnalyse validieren
    #   (Tipp: JobAnalyse.model_validate_json(...)). Was passiert, wenn das LLM
    #   ```json ... ``` drumherum schreibt? Fang das ab.
    raise NotImplementedError


def top_skills(analysen: list[JobAnalyse], n: int = 10) -> list[tuple[str, int]]:
    """Zählt, welche Muss-Skills am häufigsten vorkommen."""
    # TODO 4: mit Counter die häufigsten muss_skills über alle Anzeigen zählen
    raise NotImplementedError


def main() -> None:
    # Schritt 2: nur das Einlesen testen (noch kein Modellaufruf)
    anzeigen = lade_anzeigen()
    print(f"{len(anzeigen)} Anzeige(n) gefunden:")
    for name, text in anzeigen:
        print(f"  {name}: {text[:100]!r}")

    lebenslauf = lade_lebenslauf()
    print(f"Lebenslauf: {len(lebenslauf)} Zeichen")

    # Ursprünglicher Ablauf, kommt in späteren Schritten zurück:
    # analysen = []
    # for name, text in anzeigen:
    #     print(f"Analysiere {name} ...")
    #     analyse = analysiere(text)
    #     analysen.append(analyse)
    #     print(json.dumps(analyse.model_dump(), indent=2, ensure_ascii=False))
    #
    # print("\nTop-Skills über alle Anzeigen:")
    # for skill, anzahl in top_skills(analysen):
    #     print(f"  {skill}: {anzahl}x")


if __name__ == "__main__":
    main()
