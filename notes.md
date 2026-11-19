# Lernnotizen

Hier erkläre ich Konzepte in eigenen Worten (3–5 Sätze je Begriff).

## Token
Ein Token ist ein Wort oder ein Wortteil. Wir sehen Text als Wörter, die KI arbeitet aber mit Tokens. Sowohl meine Eingabe als auch die Antwort des Modells bestehen aus Tokens, und das Modell schreibt die Antwort Token für Token nacheinander. Die Dauer hängt deshalb von der Anzahl ab: Mein Laptop schafft etwa 7 Tokens pro Sekunde. Mit Thinking schrieb das Modell erst über 1200 unsichtbare Tokens zum Nachdenken (1284 Tokens, 3 Minuten), ohne Thinking nur 91 Tokens (12 Sekunden), bei gleich guter Antwort.

## Embedding
_TODO_

## RAG (Retrieval-Augmented Generation)
_TODO: Was ist es und welches Problem löst es?_

## Prompting vs. RAG vs. Fine-Tuning
_TODO: Wann nutze ich was?_

## Strukturierte Ausgabe (JSON-Schema / Pydantic)
Ein Programm braucht von der KI immer dasselbe feste Format, damit es die Werte an genau den richtigen Stellen lesen und damit weiterarbeiten kann. Das Modell soll deshalb nicht frei schreiben. Pydantic ist ein Python-Paket, das die Antwort mit dem Schema vergleicht: Sind alle Felder da, stimmt der Typ (Zahl statt Text), liegt der Wert im erlaubten Bereich (passung 0 bis 10)? Erst wenn das stimmt, geht es weiter. Für Agenten ist das wichtig, weil jeder Schritt seine Daten immer an derselben Stelle liefert und der nächste Schritt sie leicht findet.

## Beobachtungen aus dem Projekt (19.11.2026)
- Lokales Modell qwen3.5:4b auf CPU: ca. 90 s pro Analyse
- Fehler: erfindet Firmenname statt null
- Fehler: setzt Azure DevOps mit Azure gleich
- Fehler: bewertet "Grundkenntnisse" wie volle Kenntnisse
