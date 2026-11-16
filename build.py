"""Erzeugt schliessungen.ics und index.html aus data/schliessungen.json.

Aufruf:  python3 build.py

Format eines Eintrags (siehe README.md):
  {"bad": "Schwimmoper", "status": "geschlossen", "grund": "Wettkampf",
   "von": "04.12.2026 08:00", "bis": "07.12.2026", "hinweis": "DMSJ-Bundesfinale."}
"""
import html
import json
import re
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "schliessungen.json"

ADRESSEN = {
    "Schwimmoper": "Schwimmoper, Südstraße 29, 42103 Wuppertal",
    "Gartenhallenbad Langerfeld": "Gartenhallenbad Langerfeld, Am Timpen 51, 42389 Wuppertal",
    "Gartenhallenbad Cronenberg": "Gartenhallenbad Cronenberg, Zum Tal, 42349 Wuppertal",
    "Schwimmsportleistungszentrum": "Schwimmsportleistungszentrum, Küllenhahner Straße 130, 42349 Wuppertal",
    "Stadtbad Uellendahl": "Stadtbad Uellendahl, Röttgen 149, 42109 Wuppertal",
    "Freibad Mählersbeck": "Freibad Mählersbeck, Mählersbeck 71, 42279 Wuppertal",
    "Alle Hallenbäder": "Wuppertal",
    "Hallenbäder": "Wuppertal",
}
STATUS = ("geschlossen", "verkürzt geöffnet", "eingeschränkt geöffnet")
WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
TAGNAMEN = {"Mo": "montags", "Di": "dienstags", "Mi": "mittwochs", "Do": "donnerstags", "Fr": "freitags", "Sa": "samstags", "So": "sonntags"}
ICS_TAGE = {"Mo": "MO", "Di": "TU", "Mi": "WE", "Do": "TH", "Fr": "FR", "Sa": "SA", "So": "SU"}

RE_DATUM = re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$")
RE_DATUM_ZEIT = re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4}),?\s+(\d{1,2})[:.](\d{2})(?:\s*Uhr)?$")
RE_ZEIT = re.compile(r"^(\d{1,2})[:.](\d{2})(?:\s*Uhr)?$")


class Eingabefehler(Exception):
    pass


def lies_zeitpunkt(text, nr, feld, bezugstag=None):
    """'04.12.2026' -> (date, None); '04.12.2026 08:00' -> (date, time); '14:00' -> (bezugstag, time)."""
    t = str(text).strip()
    try:
        if m := RE_DATUM_ZEIT.match(t):
            tag, mon, jahr, h, mi = map(int, m.groups())
            return date(jahr, mon, tag), time(h, mi)
        if m := RE_DATUM.match(t):
            tag, mon, jahr = map(int, m.groups())
            return date(jahr, mon, tag), None
        if (m := RE_ZEIT.match(t)) and bezugstag:
            h, mi = map(int, m.groups())
            return bezugstag, time(h, mi)
    except ValueError:
        raise Eingabefehler(f"Eintrag {nr}: „{feld}“ = „{t}“ ist kein gültiges Datum oder keine gültige Uhrzeit.")
    raise Eingabefehler(
        f"Eintrag {nr}: „{feld}“ = „{t}“ nicht verstanden. Erlaubt: „TT.MM.JJJJ“ oder „TT.MM.JJJJ HH:MM“"
        + (" oder nur „HH:MM“ (gleicher Tag wie „von“)." if feld == "bis" else ".")
    )


def tag_text(d):
    return f"{WOCHENTAGE[d.weekday()]} {d:%d.%m.%Y}"


def zeit_text(t):
    return f"{t:%H:%M} Uhr"


def normalisiere(e, nr):
    """Wandelt einen von Hand geschriebenen Eintrag in das interne Format um."""
    for feld in ("bad", "status", "grund", "von"):
        if not str(e.get(feld, "")).strip():
            raise Eingabefehler(f"Eintrag {nr}: Feld „{feld}“ fehlt.")
    if e["bad"] not in ADRESSEN:
        raise Eingabefehler(f"Eintrag {nr}: Bad „{e['bad']}“ unbekannt. Erlaubt: {', '.join(ADRESSEN)}.")
    if e["status"] not in STATUS:
        raise Eingabefehler(f"Eintrag {nr}: Status „{e['status']}“ unbekannt. Erlaubt: {', '.join(STATUS)}.")

    von_tag, von_zeit = lies_zeitpunkt(e["von"], nr, "von")
    bis_tag, bis_zeit = lies_zeitpunkt(e.get("bis") or e["von"].split()[0], nr, "bis", bezugstag=von_tag)
    hinweis = str(e.get("hinweis", "")).strip()

    ganztaegig = von_zeit is None and bis_zeit is None
    if ganztaegig:
        start_dt, ende_dt = von_tag, bis_tag + timedelta(days=1)
        start, ende = f"{start_dt:%Y%m%d}", f"{ende_dt:%Y%m%d}"
        zeitraum = (f"Am {tag_text(von_tag)}" if von_tag == bis_tag
                    else f"Von {tag_text(von_tag)} bis einschließlich {tag_text(bis_tag)}")
    else:
        start_dt = datetime.combine(von_tag, von_zeit or time(0, 0))
        if bis_zeit is None:  # ganzer letzter Tag
            ende_dt = datetime.combine(bis_tag + timedelta(days=1), time(0, 0))
        else:
            ende_dt = datetime.combine(bis_tag, bis_zeit)
        start, ende = f"{start_dt:%Y%m%dT%H%M%S}", f"{ende_dt:%Y%m%dT%H%M%S}"
        if von_tag == bis_tag and von_zeit and bis_zeit:
            zeitraum = f"Am {tag_text(von_tag)} von {von_zeit:%H:%M} bis {bis_zeit:%H:%M} Uhr"
        else:
            links = f"{tag_text(von_tag)}, {zeit_text(von_zeit)}" if von_zeit else f"{tag_text(von_tag)} ganztägig"
            rechts = f"{tag_text(bis_tag)}, {zeit_text(bis_zeit)}" if bis_zeit else f"einschließlich {tag_text(bis_tag)}"
            zeitraum = f"Von {links} bis {rechts}"
    if ende_dt <= start_dt:
        raise Eingabefehler(f"Eintrag {nr}: „bis“ liegt vor „von“.")

    wiederholung = None
    w = e.get("wiederholung")
    if w:
        tage = w.get("tage") or []
        if not tage or any(t not in ICS_TAGE for t in tage):
            raise Eingabefehler(f"Eintrag {nr}: „wiederholung.tage“ muss eine Liste wie [\"Sa\", \"So\"] sein.")
        bis_w, _ = lies_zeitpunkt(w.get("bis", ""), nr, "wiederholung.bis")
        until = datetime.combine(bis_w + timedelta(days=1), time(0, 0)) - timedelta(hours=2)  # Ende des Tages, UTC
        wiederholung = f"FREQ=WEEKLY;BYDAY={','.join(ICS_TAGE[t] for t in tage)};UNTIL={until:%Y%m%dT%H%M%S}Z"
        namen = [TAGNAMEN[t] for t in tage]
        aufzaehlung = namen[0] if len(namen) == 1 else ", ".join(namen[:-1]) + " und " + namen[-1]
        zeitraum = f"{aufzaehlung[0].upper()}{aufzaehlung[1:]} vom {von_tag:%d.%m.%Y} bis {bis_w:%d.%m.%Y}"

    if e["status"] != "geschlossen" and not wiederholung:
        # Bei verkürzter Öffnung zählt der Tag, nicht der weggefallene Zeitraum.
        zeitraum = (f"Am {tag_text(von_tag)}" if von_tag == bis_tag
                    else f"Von {tag_text(von_tag)} bis einschließlich {tag_text(bis_tag)}")

    if e["status"] == "geschlossen":
        beschreibung = f"{zeitraum} geschlossen." + (f" {hinweis}" if hinweis else "")
    else:
        beschreibung = f"{zeitraum}: {hinweis}" if hinweis else f"{zeitraum} {e['status']}."

    return {
        "bad": e["bad"], "status": e["status"], "grund": e["grund"],
        "start": start, "ende": ende, "ganztaegig": ganztaegig,
        "beschreibung": beschreibung, "wiederholung": wiederholung,
    }


VTIMEZONE = [
    "BEGIN:VTIMEZONE", "TZID:Europe/Berlin",
    "BEGIN:DAYLIGHT", "TZOFFSETFROM:+0100", "TZOFFSETTO:+0200", "TZNAME:CEST",
    "DTSTART:19700329T020000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU", "END:DAYLIGHT",
    "BEGIN:STANDARD", "TZOFFSETFROM:+0200", "TZOFFSETTO:+0100", "TZNAME:CET",
    "DTSTART:19701025T030000", "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU", "END:STANDARD",
    "END:VTIMEZONE",
]


def esc(s):
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def fold(line):
    out, cur = [], b""
    for ch in line:
        c = ch.encode("utf-8")
        if len(cur) + len(c) > (75 if not out else 74):
            out.append(cur)
            cur = b""
        cur += c
    out.append(cur)
    return "\r\n ".join(x.decode("utf-8") for x in out)


def uid(e):
    raw = f"{e['start']}-{e['bad']}-{e['grund']}"
    return "".join(c if c.isalnum() else "-" for c in raw).lower() + "@baeder-wuppertal"


def build_ics(eintraege):
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Baeder Wuppertal//DE", "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH", "X-WR-CALNAME:Schwimmbäder Wuppertal – Schließungen", "X-WR-TIMEZONE:Europe/Berlin",
        "X-WR-CALDESC:" + esc("Schließungen und verkürzte Öffnungszeiten der städtischen Schwimmbäder in Wuppertal. KI-gestützt und automatisiert erfasst, daher möglicherweise fehlerhaft oder unvollständig. Verbindlich sind die Angaben der Stadt Wuppertal. Ohne Gewähr."),
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H", "X-PUBLISHED-TTL:PT1H",
        *VTIMEZONE,
    ]
    seen = set()
    for e in eintraege:
        u = uid(e)
        if u in seen:
            raise Eingabefehler(f"Doppelter Eintrag: {e['bad']}, {e['grund']}, Beginn {e['start']}.")
        seen.add(u)
        if e["ganztaegig"]:
            start, ende = f"DTSTART;VALUE=DATE:{e['start']}", f"DTEND;VALUE=DATE:{e['ende']}"
        else:
            start, ende = f"DTSTART;TZID=Europe/Berlin:{e['start']}", f"DTEND;TZID=Europe/Berlin:{e['ende']}"
        lines += ["BEGIN:VEVENT", f"UID:{u}", f"DTSTAMP:{now}", start, ende]
        if e.get("wiederholung"):
            lines.append("RRULE:" + e["wiederholung"])
        lines += [
            "SUMMARY:" + esc(f"{e['bad']}: {e['status']} ({e['grund']})"),
            "LOCATION:" + esc(ADRESSEN.get(e["bad"], "Wuppertal")),
            "DESCRIPTION:" + esc(e["beschreibung"]),
            "TRANSP:TRANSPARENT", "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    (ROOT / "schliessungen.ics").write_text("\r\n".join(fold(x) for x in lines) + "\r\n", encoding="utf-8", newline="")


def build_html(eintraege):
    daten = json.dumps(eintraege, ensure_ascii=False)
    noscript = "\n".join(
        f"<li><strong>{html.escape(e['bad'])}: {html.escape(e['status'])} ({html.escape(e['grund'])})</strong><br>{html.escape(e['beschreibung'])}</li>"
        for e in eintraege
    )
    vorlage = (ROOT / "vorlage.html").read_text(encoding="utf-8")
    seite = vorlage.replace("{{DATEN}}", daten).replace("{{NOSCRIPT}}", noscript)
    (ROOT / "index.html").write_text(seite, encoding="utf-8")


def main():
    roh = json.loads(DATA.read_text(encoding="utf-8"))
    try:
        eintraege = [normalisiere(e, nr) for nr, e in enumerate(roh, start=1)]
        eintraege.sort(key=lambda e: e["start"])
        build_ics(eintraege)
        build_html(eintraege)
    except Eingabefehler as err:
        sys.exit(f"Fehler: {err}")
    print(f"{len(eintraege)} Einträge geschrieben.")


if __name__ == "__main__":
    main()
