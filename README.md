# Schwimmbäder Wuppertal – Schließungen

Schließungen und verkürzte Öffnungszeiten der städtischen Schwimmbäder in Wuppertal an einem Ort: als Webseite und als Kalender zum Abonnieren.

## Dateien

- `data/schliessungen.json`: alle Einträge (die einzige Datei, die bei Änderungen bearbeitet wird)
- `build.py`: erzeugt daraus `schliessungen.ics` und `index.html`
- `schliessungen.ics`: Kalender zum Abonnieren
- `index.html`: Webseite mit Abo-Knöpfen und Liste der Schließungen

## Eintrag ändern oder ergänzen

1. Eintrag in `data/schliessungen.json` anlegen oder ändern
2. `python3 build.py` ausführen
3. Alle Dateien committen und pushen

Ein Eintrag sieht so aus:

```json
{
  "bad": "Schwimmoper",
  "status": "geschlossen",
  "grund": "Wettkampf",
  "start": "20261204T080000",
  "ende": "20261208T000000",
  "ganztaegig": false,
  "beschreibung": "Von Fr 04.12.2026, 08:00 Uhr bis einschließlich Mo 07.12.2026 geschlossen. DMSJ-Bundesfinale."
}
```

- `status`: `geschlossen`, `verkürzt geöffnet` oder `eingeschränkt geöffnet`
- `grund`: z. B. `Wartung`, `Sanierung`, `Wettkampf`, `Veranstaltung`, `Personalmangel`, `Personaleinsatz im Freibad`, `Wetter`, `Feiertag: <Name>`
- Ganztägig: `start`/`ende` als `JJJJMMTT`, `ende` ist der Tag **nach** dem letzten Schließtag
- Mit Uhrzeit: `JJJJMMTTTHHMMSS` in deutscher Ortszeit

Alle Angaben ohne Gewähr.
