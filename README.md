# Job-Anzeigen-Analyzer

Ein Python-Tool, das Stellenanzeigen mit einem lokalen Large Language Model (LLM) analysiert und mit einem Lebenslauf abgleicht. Es extrahiert Jobtitel, Muss- und Nice-to-have-Skills, Remote-Option und Seniority als validiertes JSON, bewertet die Passung von 0 bis 10 mit Begründung und schreibt auf Wunsch einen Anschreiben-Entwurf.

## Warum dieses Projekt?
Ich bewerbe mich auf KI-Stellen und wollte datenbasiert sehen, welche Fähigkeiten der Markt verlangt und wie gut ein kleines lokales Modell eine Stelle einschätzen kann – gemessen an meiner eigenen Bewertung statt nach Gefühl.

## Features
- [x] Stellenanzeigen und Lebenslauf aus Textdateien einlesen
- [x] Anforderungen per LLM als JSON extrahieren und mit **Pydantic** validieren (inkl. Wiederholung bei ungültigem JSON)
- [x] Abgleich mit dem Lebenslauf: erfüllt / fehlt, Passung 0–10 mit Begründung
- [x] Anschreiben-Entwurf nach festen Schreibregeln
- [x] Kommandozeile (`argparse`): einzelne Anzeige, alle Anzeigen, Top-Skills über alle Anzeigen
- [x] **Eval-Skript**: Modell-Bewertung gegen meine eigene Bewertung von 10 echten Anzeigen, Ergebnisse als CSV
- [x] 19 Tests mit pytest

## Nächste Schritte
- Größeres Modell vergleichen (z. B. 9B) und den Prompt weiter verbessern
- Einfache Weboberfläche (Streamlit)

## Tech-Stack
Python 3.12 · Ollama (lokal, qwen3.5:4b) · Pydantic · pytest · python-dotenv

Das Modell läuft komplett lokal auf meinem Laptop (CPU, ohne Grafikkarte). Es fallen keine API-Kosten an, und der Lebenslauf verlässt den Rechner nicht. Die echte Lebenslauf-Datei ist per `.gitignore` geschützt, im Repo liegt nur eine erfundene Vorlage.

## Installation
```bash
git clone https://github.com/Atul1700/analyzer.git
cd analyzer
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Modellname steht dort in MODEL
# Ollama installieren (https://ollama.com), dann das Modell laden:
ollama pull qwen3.5:4b
cp data/lebenslauf_beispiel.txt data/lebenslauf.txt   # eigene Daten eintragen
```

## Verwendung
```bash
python analyzer.py                              # erste Anzeige aus data/jobs/
python analyzer.py data/jobs/beispiel_01.txt    # genau diese Anzeige
python analyzer.py --ohne-anschreiben           # nur Analyse, spart Zeit
python analyzer.py --alle --ohne-anschreiben    # alle Anzeigen + häufigste Skills
python eval.py                                  # Modell gegen eigene Bewertung messen
pytest                                          # Tests
```

## Ergebnisse (Eval mit 10 echten Anzeigen)
Ich habe 10 Stellenanzeigen selbst von 0 bis 10 bewertet und das Modell dieselben Anzeigen bewerten lassen.

| Lauf | Änderung | Mittlere Abweichung | Treffer ±1 | Treffer ±2 |
|---|---|---|---|---|
| 1 | Prompt ohne Skala | 2,6 Punkte | 2 von 10 | 6 von 10 |
| 2 | Skala-Anker im Prompt + Begründung im Ergebnis | 1,9 Punkte | 3 von 10 | 8 von 10 |

- In Lauf 1 war das Modell **bei allen 10 Anzeigen zu optimistisch** (bis zu +5).
- Mit klar beschriebenen Stufen („6–7: Kern erfüllt, mit einzelnen Lücken“ usw.) sank die Abweichung um rund 27 %, und das Modell liegt jetzt nicht mehr nur nach oben daneben.
- Eine Analyse dauert lokal etwa 1–3 Minuten.

## Was ich dabei gelernt habe
- **Strukturierte Ausgabe ist die Grundlage:** Erst mit einem festen Schema und Validierung kann ein Programm zuverlässig mit LLM-Antworten weiterarbeiten.
- **Ohne Messung kein Urteil:** Erst das Eval-Set hat gezeigt, dass das Modell systematisch zu gut bewertet. Eine Prompt-Änderung kann ich jetzt mit Zahlen prüfen statt nach Gefühl.
- **Kleine Modelle erfinden Dinge:** Das 4B-Modell hat Firmennamen erfunden, „Azure DevOps“ mit „Azure“ gleichgesetzt und im Anschreiben Berufsjahre dazugedichtet. Regeln im Prompt helfen, ersetzen aber nicht die Prüfung durch einen Menschen.
- **Reproduzierbarkeit:** Mit `temperature=0` liefert dieselbe Eingabe dieselbe Analyse – wichtig, um Änderungen fair zu vergleichen.

Weitere Notizen: [notes.md](notes.md)