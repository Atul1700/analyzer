# Job-Anzeigen-Analyzer

Ein Python-Tool, das KI-Stellenanzeigen mit einem Large Language Model (LLM) analysiert: Es extrahiert Jobtitel, Muss- und Nice-to-have-Skills, Remote-Option und Seniority als strukturiertes JSON und zeigt, welche Skills am häufigsten verlangt werden.

**Status:** in Arbeit (Projekt 1 von 4 meines KI-Portfolios)

## Warum dieses Projekt?
Ich bewerbe mich auf KI-Stellen und wollte datenbasiert herausfinden, welche Fähigkeiten der Markt wirklich verlangt, statt zu raten.

## Features
- [ ] Stellenanzeigen aus Textdateien einlesen
- [ ] Anforderungen per LLM als validiertes JSON extrahieren (Pydantic)
- [ ] Häufigste Skills über alle Anzeigen auswerten
- [ ] Ergebnisse als CSV exportieren
- [ ] Einfache Weboberfläche (Streamlit)

## Tech-Stack
Python 3.12 · Anthropic API · Pydantic · python-dotenv

## Installation
```bash
git clone https://github.com/Atul1700/analyzer.git
cd analyzer
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # dann deinen API-Key in .env eintragen
python analyzer.py
```

## Ergebnisse
_Folgt, sobald die ersten Anzeigen ausgewertet sind._

## Was ich dabei gelernt habe
_Folgt._
