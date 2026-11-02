"""
Job-Anzeigen-Analyzer
---------------------
Liest Stellenanzeigen (Textdateien in data/jobs/), lässt ein LLM die
Anforderungen als strukturiertes JSON extrahieren und zählt am Ende,
welche Skills am häufigsten verlangt werden.

Lernziele: Python-Grundlagen, LLM-API, strukturierte Ausgabe mit Pydantic.
Die Stellen mit "TODO" füllst DU aus.
"""

import json
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
import anthropic

load_dotenv()  # liest ANTHROPIC_API_KEY aus der Datei .env (nie ins Repo!)

MODEL = "claude-sonnet-4-5"  # TODO: aktuelles Modell in der Anthropic-Doku nachschlagen
JOBS_DIR = Path("data/jobs")


class JobAnalyse(BaseModel):
    """Das Schema, das das LLM zurückgeben soll."""
    jobtitel: str
    firma: str | None
    muss_skills: list[str]
    nice_to_have: list[str]
    remote_moeglich: bool | None
    seniority: str | None  # z. B. "Junior", "Mid", "Senior"


def lade_anzeigen() -> dict[str, str]:
    """Gibt {dateiname: text} für alle .txt-Dateien in data/jobs/ zurück."""
    # TODO 1: alle *.txt-Dateien in JOBS_DIR einlesen (Tipp: JOBS_DIR.glob("*.txt"), .read_text(encoding="utf-8"))
    raise NotImplementedError


def baue_prompt(anzeigentext: str) -> str:
    """Erstellt den Prompt für das LLM."""
    # TODO 2: Schreibe einen klaren Prompt. Er soll:
    #   - die Aufgabe erklären (Anforderungen extrahieren)
    #   - NUR JSON nach dem Schema von JobAnalyse verlangen
    #   - Skills normalisieren (z. B. "Python 3" -> "Python")
    #   - den Anzeigentext enthalten
    raise NotImplementedError


def analysiere(client: anthropic.Anthropic, anzeigentext: str) -> JobAnalyse:
    """Schickt eine Anzeige ans LLM und gibt das validierte Ergebnis zurück."""
    antwort = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": baue_prompt(anzeigentext)}],
    )
    rohtext = antwort.content[0].text
    # TODO 3: rohtext als JSON parsen und mit JobAnalyse validieren
    #   (Tipp: JobAnalyse.model_validate_json(...)). Was passiert, wenn das LLM
    #   ```json ... ``` drumherum schreibt? Fang das ab.
    raise NotImplementedError


def top_skills(analysen: list[JobAnalyse], n: int = 10) -> list[tuple[str, int]]:
    """Zählt, welche Muss-Skills am häufigsten vorkommen."""
    # TODO 4: mit Counter die häufigsten muss_skills über alle Anzeigen zählen
    raise NotImplementedError


def main() -> None:
    client = anthropic.Anthropic()
    anzeigen = lade_anzeigen()
    analysen = []
    for name, text in anzeigen.items():
        print(f"Analysiere {name} ...")
        analyse = analysiere(client, text)
        analysen.append(analyse)
        print(json.dumps(analyse.model_dump(), indent=2, ensure_ascii=False))

    print("\nTop-Skills über alle Anzeigen:")
    for skill, anzahl in top_skills(analysen):
        print(f"  {skill}: {anzahl}x")


if __name__ == "__main__":
    main()
