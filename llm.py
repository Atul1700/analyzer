"""
Modell-Schicht
--------------
Einziger Ort im Projekt, der mit dem LLM spricht. Der Rest des Codes ruft nur
frage_modell() auf. Wenn du das Modell oder den Anbieter wechselst, aenderst
du nur diese Datei (und MODEL in der .env).
"""

import os
import time

import ollama
from dotenv import load_dotenv

load_dotenv()  # liest MODEL aus der Datei .env

MODEL = os.getenv("MODEL", "qwen3.5:4b")


def frage_modell(prompt: str) -> str:
    """Schickt den Prompt an das lokale Ollama-Modell und gibt nur den Antworttext zurueck."""
    try:
        antwort = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            think=False,  # kein "Denktext" vor der Antwort (stoert sonst das JSON-Parsen)
        )
    except ConnectionError as fehler:
        raise RuntimeError(
            "Ollama ist nicht erreichbar. Starte die Ollama-App "
            "bzw. 'ollama serve' und versuche es erneut."
        ) from fehler
    except ollama.ResponseError as fehler:
        if fehler.status_code == 404:
            raise RuntimeError(
                f"Das Modell '{MODEL}' ist nicht installiert. "
                f"Lade es mit: ollama pull {MODEL}"
            ) from fehler
        raise RuntimeError(f"Ollama meldet einen Fehler: {fehler.error}") from fehler

    return antwort.message.content or ""


if __name__ == "__main__":
    frage = "Was ist die Hauptstadt von Oesterreich? Antworte in einem Satz."
    print(f"Modell: {MODEL}")
    print(f"Frage:  {frage}")
    start = time.perf_counter()
    text = frage_modell(frage)
    dauer = time.perf_counter() - start
    print(f"Antwort: {text}")
    print(f"Dauer:   {dauer:.1f} Sekunden")
