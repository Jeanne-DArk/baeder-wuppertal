# Schwimmbäder Wuppertal – Schließungen

Schließungen und verkürzte Öffnungszeiten der städtischen Schwimmbäder in Wuppertal an einem Ort: als Webseite und als Kalender zum Abonnieren.

## Dateien

- `data/schliessungen.json`: alle Einträge. Nur diese Datei wird bei Änderungen bearbeitet.
- `build.py`: erzeugt daraus `schliessungen.ics` und `index.html`
- `vorlage.html`: Vorlage für die Webseite
- `schliessungen.ics`: Kalender zum Abonnieren (wird erzeugt)
- `index.html`: Webseite (wird erzeugt)

## Eintrag ändern oder ergänzen

1. Eintrag in `data/schliessungen.json` anlegen oder ändern
2. `python3 build.py` ausführen. Bei Tippfehlern meldet das Skript, welcher Eintrag nicht stimmt.
3. Alle Dateien committen und pushen

### Beispiele

Ganzer Tag:

```json
{ "bad": "Stadtbad Uellendahl", "status": "geschlossen", "grund": "Veranstaltung", "von": "16.07.2026" }
```

Mehrere ganze Tage (`bis` ist der letzte Schließtag, einschließlich):

```json
{ "bad": "Schwimmoper", "status": "geschlossen", "grund": "Wartung", "von": "18.07.2026", "bis": "30.08.2026" }
```

Mit Uhrzeit, über mehrere Tage:

```json
{ "bad": "Schwimmoper", "status": "geschlossen", "grund": "Wettkampf",
  "von": "10.11.2026 08:00", "bis": "17.11.2026 14:00", "hinweis": "Deutsche Kurzbahnmeisterschaften." }
```

Ab einer Uhrzeit bis einschließlich eines späteren Tages:

```json
{ "bad": "Schwimmoper", "status": "geschlossen", "grund": "Wettkampf",
  "von": "04.12.2026 08:00", "bis": "07.12.2026", "hinweis": "DMSJ-Bundesfinale." }
```

Am selben Tag (bei `bis` reicht die Uhrzeit):

```json
{ "bad": "Schwimmsportleistungszentrum", "status": "geschlossen", "grund": "Personaleinsatz im Freibad",
  "von": "27.05.2026 18:00", "bis": "21:00" }
```

Verkürzt geöffnet (`von`/`bis` = der Zeitraum, der wegfällt; die tatsächlichen Öffnungszeiten stehen im Hinweis):

```json
{ "bad": "Schwimmoper", "status": "verkürzt geöffnet", "grund": "Personaleinsatz im Freibad",
  "von": "26.05.2026 14:00", "bis": "22:00",
  "hinweis": "Schwimmhalle und Fitness nur bis 14:00 Uhr geöffnet, Sauna ganztägig geschlossen." }
```

Jede Woche wiederkehrend:

```json
{ "bad": "Schwimmoper", "status": "verkürzt geöffnet", "grund": "Personaleinsatz im Freibad",
  "von": "09.05.2026 15:00", "bis": "18:00",
  "wiederholung": { "tage": ["Sa", "So"], "bis": "12.07.2026" },
  "hinweis": "Nur von 9:00 bis 15:00 Uhr geöffnet." }
```

### Felder

| Feld | Pflicht | Inhalt |
| --- | --- | --- |
| `bad` | ja | `Schwimmoper`, `Gartenhallenbad Langerfeld`, `Gartenhallenbad Cronenberg`, `Schwimmsportleistungszentrum`, `Stadtbad Uellendahl`, `Freibad Mählersbeck`, `Alle Hallenbäder` oder `Hallenbäder` |
| `status` | ja | `geschlossen`, `verkürzt geöffnet` oder `eingeschränkt geöffnet` |
| `grund` | ja | z. B. `Wartung`, `Sanierung`, `Wettkampf`, `Veranstaltung`, `Personalmangel`, `Personaleinsatz im Freibad`, `Wetter`, `Feiertag: <Name>` |
| `von` | ja | `TT.MM.JJJJ` oder `TT.MM.JJJJ HH:MM` |
| `bis` | nein | `TT.MM.JJJJ`, `TT.MM.JJJJ HH:MM` oder nur `HH:MM` (gleicher Tag wie `von`). Fehlt es, gilt nur der Tag von `von`. Ohne Uhrzeit ist der ganze Tag gemeint. |
| `hinweis` | nein | Zusätzliche Information, z. B. der Anlass oder die tatsächlichen Öffnungszeiten |
| `wiederholung` | nein | `{ "tage": ["Sa", "So"], "bis": "TT.MM.JJJJ" }` |

Die Beschreibung im Kalender („Von Fr 04.12.2026, 08:00 Uhr bis einschließlich Mo 07.12.2026 geschlossen.“) erzeugt das Skript selbst.

Alle Angaben ohne Gewähr.
