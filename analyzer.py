"""
Job-Anzeigen-Analyzer
---------------------
Liest Stellenanzeigen (Textdateien in data/jobs/), lässt ein LLM die
Anforderungen als strukturiertes JSON extrahieren und zählt am Ende,
welche Skills am häufigsten verlangt werden.

Lernziele: Python-Grundlagen, lokales LLM (Ollama), strukturierte Ausgabe mit Pydantic.
Die Stellen mit "TODO" füllst DU aus.
"""

import argparse
import json
import re
import time
from collections import Counter
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

import llm

JOBS_DIR = Path("data/jobs")
LEBENSLAUF_DATEI = Path("data/lebenslauf.txt")
SCHREIBREGELN_DATEI = Path("data/schreibregeln.txt")


class JobAnalyse(BaseModel):
    """Das Schema, das das LLM zurückgeben soll."""
    jobtitel: str
    firma: str | None
    muss_skills: list[str]
    nice_to_have: list[str]
    remote_moeglich: bool | None
    seniority: str | None  # z. B. "Junior", "Mid", "Senior"
    # Abgleich mit dem Lebenslauf. Reihenfolge ist Absicht: erst auflisten, dann bewerten.
    erfuellt: list[str]  # Anforderungen der Anzeige, die der Lebenslauf abdeckt
    fehlt: list[str]  # Anforderungen der Anzeige, die im Lebenslauf fehlen
    passung: int = Field(ge=0, le=10)  # 0 = passt gar nicht, 10 = passt perfekt
    begruendung: str  # 1-2 Sätze


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


def baue_prompt(anzeigentext: str, lebenslauf: str) -> str:
    """Erstellt den Prompt für das LLM."""
    return f"""Du bist ein Karriereberater. Analysiere die folgende Stellenanzeige und gleiche sie mit dem Lebenslauf ab.

Aufgaben:
1. Extrahiere jobtitel, firma, muss_skills, nice_to_have, remote_moeglich und seniority aus der Anzeige.
   Wenn etwas nicht in der Anzeige steht, nimm null (nichts erfinden).
2. Normalisiere Skills auf den Kernnamen (z. B. "Python 3" -> "Python", "gute Kenntnisse in SQL" -> "SQL").
3. Prüfe jede Anforderung der Anzeige gegen den Lebenslauf:
   - erfuellt: Anforderungen, die der Lebenslauf belegt
   - fehlt: Anforderungen, die im Lebenslauf nicht vorkommen
4. passung: ganze Zahl von 0 bis 10. Skala:
   - 0-1: völlig anderes Berufsfeld
   - 2-3: wenige Überschneidungen, wesentliche Muss-Anforderungen fehlen
   - 4-5: teilweise Überschneidung, mehrere Muss-Anforderungen fehlen
   - 6-7: Kern erfüllt, mit einzelnen Lücken
   - 8-9: fast alle Muss-Anforderungen erfüllt
   - 10: nur wenn alle Muss-Anforderungen UND das Erfahrungsniveau passen
   Fehlende Berufserfahrung oder Seniority senkt die Zahl.
   Grundkenntnisse zählen nicht als erfüllt, wenn solide Kenntnisse verlangt sind.
5. begruendung: 1-2 Sätze auf Deutsch, warum diese Passung.

Antworte NUR mit JSON nach dem vorgegebenen Schema, ohne weiteren Text.

=== STELLENANZEIGE ===
{anzeigentext}

=== LEBENSLAUF ===
{lebenslauf}
"""


def _json_extrahieren(rohtext: str) -> str:
    """Entfernt einen ```json ... ```-Block um die Antwort, falls vorhanden."""
    treffer = re.search(r"```(?:json)?\s*(.*?)```", rohtext, re.DOTALL)
    return (treffer.group(1) if treffer else rohtext).strip()


def analysiere(anzeigentext: str, lebenslauf: str, versuche: int = 2) -> JobAnalyse:
    """Schickt Anzeige + Lebenslauf ans LLM und gibt das validierte Ergebnis zurück.

    Bei ungültigem JSON wird einmal wiederholt (versuche=2), danach kommt eine Fehlermeldung.
    """
    prompt = baue_prompt(anzeigentext, lebenslauf)
    schema = JobAnalyse.model_json_schema()
    letzter_fehler = None
    for _ in range(versuche):
        rohtext = llm.frage_modell(prompt, schema=schema)
        try:
            return JobAnalyse.model_validate_json(_json_extrahieren(rohtext))
        except ValidationError as fehler:
            letzter_fehler = fehler
    raise RuntimeError(
        f"Das Modell hat nach {versuche} Versuchen kein gültiges JSON geliefert. "
        f"Letzter Fehler: {letzter_fehler}"
    )


def schreibe_anschreiben(analyse: JobAnalyse, anzeigentext: str, lebenslauf: str) -> str:
    """Erzeugt einen Anschreiben-Entwurf als Freitext und gibt nur den Brieftext zurueck."""
    regeln = SCHREIBREGELN_DATEI.read_text(encoding="utf-8")
    prompt = f"""{regeln}

Die Analyse unten sagt, was der Lebenslauf abdeckt (erfuellt) und was fehlt.

=== ANALYSE ===
Jobtitel: {analyse.jobtitel}
Firma: {analyse.firma or "nicht genannt"}
erfuellt: {", ".join(analyse.erfuellt)}
fehlt: {", ".join(analyse.fehlt)}

=== STELLENANZEIGE ===
{anzeigentext}

=== LEBENSLAUF ===
{lebenslauf}

Gib NUR den Brieftext aus, ohne Einleitung, ohne Betreffzeile und ohne Kommentar.
"""
    # Freitext (kein Schema); 0.3 erlaubt etwas Variation im Ausdruck
    return llm.frage_modell(prompt, temperature=0.3).strip()


def top_skills(analysen: list[JobAnalyse], n: int = 10) -> list[tuple[str, int]]:
    """Zählt, welche Muss-Skills am häufigsten vorkommen."""
    # Counter zählt Vorkommen; update() addiert die Skills jeder Analyse dazu
    zaehler = Counter()
    for analyse in analysen:
        zaehler.update(analyse.muss_skills)
    # most_common(n) liefert die n häufigsten als (skill, anzahl), häufigste zuerst
    return zaehler.most_common(n)


def baue_parser() -> argparse.ArgumentParser:
    """Definiert die Kommandozeilen-Optionen (argparse gehört zur Standardbibliothek)."""
    parser = argparse.ArgumentParser(
        description=(
            "Job-Anzeigen-Analyzer: liest Stellenanzeigen, lässt ein lokales Modell die "
            "Anforderungen extrahieren, gleicht sie mit deinem Lebenslauf ab und schreibt "
            "auf Wunsch einen Anschreiben-Entwurf."
        ),
        epilog=(
            "Beispiele:\n"
            "  python analyzer.py                              erste Anzeige aus data/jobs/\n"
            "  python analyzer.py data/jobs/beispiel_01.txt    genau diese Anzeige\n"
            "  python analyzer.py --ohne-anschreiben           nur Analyse, spart Zeit\n"
            "  python analyzer.py --alle --ohne-anschreiben    alle Anzeigen + Top-Skills"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "anzeige",
        nargs="?",  # '?' = optional: ohne Angabe ist der Wert None
        type=Path,
        help="Pfad zu einer Anzeige (.txt). Ohne Angabe wird die erste Anzeige in data/jobs/ genommen.",
    )
    parser.add_argument(
        "--ohne-anschreiben",
        action="store_true",  # Schalter: True, wenn angegeben, sonst False
        help="Überspringt das Anschreiben (spart Zeit, nur die Analyse läuft).",
    )
    parser.add_argument(
        "--alle",
        action="store_true",
        help="Analysiert alle Anzeigen in data/jobs/ und gibt am Ende die häufigsten Muss-Skills aus.",
    )
    return parser


def verarbeite(name: str, text: str, lebenslauf: str, mit_anschreiben: bool) -> JobAnalyse:
    """Analysiert eine Anzeige, gibt sie aus und schreibt optional das Anschreiben."""
    print(f"Analysiere {name} ...")
    start = time.perf_counter()
    analyse = analysiere(text, lebenslauf)
    dauer = time.perf_counter() - start
    print(json.dumps(analyse.model_dump(), indent=2, ensure_ascii=False))
    print(f"Dauer Analyse: {dauer:.1f} Sekunden")

    if mit_anschreiben:
        print("\nErzeuge Anschreiben ...")
        start = time.perf_counter()
        anschreiben = schreibe_anschreiben(analyse, text, lebenslauf)
        dauer = time.perf_counter() - start
        print(anschreiben)
        print(f"Dauer Anschreiben: {dauer:.1f} Sekunden")
    return analyse


def main() -> None:
    args = baue_parser().parse_args()
    lebenslauf = lade_lebenslauf()
    mit_anschreiben = not args.ohne_anschreiben

    if args.alle and args.anzeige:
        raise SystemExit("Entweder eine einzelne Anzeige ODER --alle angeben, nicht beides.")

    if args.alle:
        analysen = []
        for name, text in lade_anzeigen():
            analysen.append(verarbeite(name, text, lebenslauf, mit_anschreiben))
            print("\n" + "=" * 60 + "\n")
        print("Top-Skills über alle Anzeigen:")
        for skill, anzahl in top_skills(analysen):
            print(f"  {skill}: {anzahl}x")
    elif args.anzeige:
        if not args.anzeige.is_file():
            raise SystemExit(f"Datei '{args.anzeige}' nicht gefunden.")
        text = args.anzeige.read_text(encoding="utf-8")
        verarbeite(args.anzeige.name, text, lebenslauf, mit_anschreiben)
    else:
        name, text = lade_anzeigen()[0]
        verarbeite(name, text, lebenslauf, mit_anschreiben)


if __name__ == "__main__":
    main()
