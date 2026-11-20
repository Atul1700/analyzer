"""
Eval-Skript
-----------
Laesst das Modell dieselben Anzeigen bewerten wie du (data/eval/meine_bewertung.csv)
und vergleicht die Zahlen. Es wird nur analysiert, kein Anschreiben erzeugt.

Beispiele:
  python eval.py                         alle Anzeigen mit dem Modell aus .env
  python eval.py --limit 2               nur die ersten 2 (zum Testen)
  python eval.py --modell qwen3.5:9b     anderes Modell, ohne die .env zu aendern
"""

import argparse
import csv
import re
import time
from pathlib import Path

import analyzer
import llm

EVAL_DIR = Path("data/eval")
BEWERTUNG_DATEI = EVAL_DIR / "meine_bewertung.csv"
ERGEBNIS_SPALTEN = ["datei", "meine_passung", "modell_passung", "begruendung", "abweichung", "dauer_s", "fehler"]


def berechne_kennzahlen(zeilen: list[dict]) -> dict:
    """Reine Funktion: berechnet die Kennzahlen aus den Ergebniszeilen.

    Jede Zeile braucht die Schluessel meine_passung, modell_passung (None bei Fehler),
    dauer_s und fehler (leer oder None, wenn alles gut ging).
    Zeilen ohne modell_passung zaehlen als Fehler und gehen nicht in die Abweichungen ein.
    """
    abweichungen = [
        abs(z["modell_passung"] - z["meine_passung"])
        for z in zeilen
        if z.get("modell_passung") is not None
    ]
    anzahl = len(abweichungen)
    return {
        "anzahl_gesamt": len(zeilen),
        "anzahl_bewertet": anzahl,
        "anzahl_fehler": len(zeilen) - anzahl,
        "mittlere_abweichung": sum(abweichungen) / anzahl if anzahl else None,
        "treffer_1": sum(a <= 1 for a in abweichungen),
        "treffer_2": sum(a <= 2 for a in abweichungen),
        "gesamtdauer_s": sum(z.get("dauer_s") or 0 for z in zeilen),
    }


def modellname_fuer_datei(modell: str) -> str:
    """Macht den Modellnamen dateinamentauglich ('qwen3.5:4b' -> 'qwen3.5_4b')."""
    return re.sub(r'[^A-Za-z0-9._-]', "_", modell)


def lese_bewertung(pfad: Path) -> list[dict]:
    """Liest meine_bewertung.csv (UTF-8, ein evtl. BOM wird ignoriert)."""
    if not pfad.is_file():
        raise SystemExit(f"Datei '{pfad}' nicht gefunden.")
    with pfad.open(encoding="utf-8-sig", newline="") as f:
        zeilen = list(csv.DictReader(f))
    for zeile in zeilen:
        try:
            zeile["meine_passung"] = int(zeile["meine_passung"])
        except (ValueError, TypeError, KeyError):
            raise SystemExit(f"Ungueltige meine_passung in Zeile fuer '{zeile.get('datei')}'.")
    return zeilen


def bewerte(zeile: dict, lebenslauf: str) -> dict:
    """Analysiert eine Anzeige und misst die Dauer. Fehler werden gespeichert, nicht geworfen."""
    ergebnis = {
        "datei": zeile["datei"],
        "meine_passung": zeile["meine_passung"],
        "modell_passung": None,
        "begruendung": "",
        "abweichung": None,
        "dauer_s": None,
        "fehler": "",
    }
    start = time.perf_counter()
    try:
        text = (analyzer.JOBS_DIR / zeile["datei"]).read_text(encoding="utf-8")
        analyse = analyzer.analysiere(text, lebenslauf)
        ergebnis["modell_passung"] = analyse.passung
        ergebnis["begruendung"] = analyse.begruendung.replace("\n", " ")
        ergebnis["abweichung"] = analyse.passung - zeile["meine_passung"]
    except Exception as fehler:  # bewusst breit: ein Fehler soll den Lauf nicht abbrechen
        ergebnis["fehler"] = f"{type(fehler).__name__}: {fehler}".replace("\n", " ")
    ergebnis["dauer_s"] = round(time.perf_counter() - start, 1)
    return ergebnis


def schreibe_ergebnis(pfad: Path, zeilen: list[dict]) -> None:
    with pfad.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ERGEBNIS_SPALTEN)
        writer.writeheader()
        for z in zeilen:
            writer.writerow({k: ("" if z[k] is None else z[k]) for k in ERGEBNIS_SPALTEN})


def drucke_zusammenfassung(zeilen: list[dict], kennzahlen: dict, modell: str, pfad: Path) -> None:
    print(f"\n{'datei':<34}{'ich':>5}{'modell':>8}{'abw.':>6}{'dauer_s':>9}  fehler")
    for z in zeilen:
        modell_p = "-" if z["modell_passung"] is None else z["modell_passung"]
        abw = "-" if z["abweichung"] is None else f"{z['abweichung']:+d}"
        print(
            f"{z['datei']:<34}{z['meine_passung']:>5}{modell_p:>8}{abw:>6}"
            f"{z['dauer_s']:>9.1f}  {z['fehler'][:60]}"
        )
    k = kennzahlen
    print(f"\nModell: {modell}")
    if k["mittlere_abweichung"] is None:
        print("Mittlere absolute Abweichung: - (keine erfolgreiche Analyse)")
    else:
        print(f"Mittlere absolute Abweichung: {k['mittlere_abweichung']:.2f}")
    print(f"Treffer innerhalb +-1: {k['treffer_1']} von {k['anzahl_gesamt']}")
    print(f"Treffer innerhalb +-2: {k['treffer_2']} von {k['anzahl_gesamt']}")
    print(f"Gesamtdauer: {k['gesamtdauer_s']:.1f} Sekunden")
    print(f"Fehler: {k['anzahl_fehler']}")
    print(f"Ergebnis gespeichert in {pfad}")


def baue_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Vergleicht die Passungs-Bewertung des Modells mit deiner eigenen."
    )
    parser.add_argument("--modell", help="Modellname fuer diesen Lauf (ueberschreibt MODEL aus .env).")
    parser.add_argument("--limit", type=int, help="Nur die ersten N Anzeigen auswerten.")
    return parser


def main() -> None:
    args = baue_parser().parse_args()
    if args.modell:
        llm.MODEL = args.modell  # llm.frage_modell liest MODEL bei jedem Aufruf
    if args.limit is not None and args.limit < 1:
        raise SystemExit("--limit muss mindestens 1 sein.")

    zeilen_in = lese_bewertung(BEWERTUNG_DATEI)
    if args.limit:
        zeilen_in = zeilen_in[: args.limit]
    lebenslauf = analyzer.lade_lebenslauf()

    ergebnisse = []
    for i, zeile in enumerate(zeilen_in, 1):
        print(f"[{i}/{len(zeilen_in)}] {zeile['datei']} ...", flush=True)
        ergebnisse.append(bewerte(zeile, lebenslauf))

    pfad = EVAL_DIR / f"ergebnis_{modellname_fuer_datei(llm.MODEL)}.csv"
    schreibe_ergebnis(pfad, ergebnisse)
    drucke_zusammenfassung(ergebnisse, berechne_kennzahlen(ergebnisse), llm.MODEL, pfad)


if __name__ == "__main__":
    main()
