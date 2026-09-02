#!/usr/bin/env python3
"""
pausen_scan.py — Sprechpausen adaptiv finden und geplante Schnitte dagegen prüfen.

WARUM DIESES SKRIPT EXISTIERT
-----------------------------
"Schnitte gehören in die Sprechpause, nie auf den Wortanfang" ist die wichtigste
Regel des Systems (references/schnitt-regeln.md) — und war bis v0.8.0 die einzige
wichtige Regel OHNE maschinelles Gate. Verschluckte Silben ("Zweitens" -> "weitens")
wurden erst beim Ansehen entdeckt, also nach dem Render.

Dieses Skript macht die Regel prüfbar: es misst, wo im Material wirklich Stille ist,
und beantwortet für jeden geplanten Schnitt die Frage "liegt der auf Sprache?".

WARUM ADAPTIVER SCHWELLWERT
---------------------------
Eine feste Rauschschwelle (-30 dB o. ä.) ist bei leisen Aufnahmen blind und bei
lauten überempfindlich — sie findet entweder gar keine oder überall Pausen.
Deshalb zwei Durchläufe: erst `loudnorm` in JSON-Modus messen (liefert die
EBU-R128-Gating-Schwelle `input_thresh` des konkreten Materials), dann
`silencedetect` mit genau dieser Schwelle. Damit passt sich die Erkennung an
jede Aufnahmesituation an, statt eine Konstante zu unterstellen.

PERFORMANCE-ENTSCHEIDUNGEN
--------------------------
- Alles, was O(Videolänge) ist, macht ffmpeg in C. Python sieht nur die
  Ereignisliste (typisch 10-200 Pausen), also O(Pausen) statt O(Frames).
  Bei 10x längerem Material wächst nur die ffmpeg-Zeit linear, der Python-Teil
  bleibt praktisch konstant.
- Zwei ffmpeg-Durchläufe, kein dritter: die Sprechfenster werden aus den Pausen
  invertiert statt separat gemessen.
- Kein Dekodieren des Videobildes (`-vn` bzw. `-map 0:a`) — nur die Audiospur.

ABHÄNGIGKEITEN
--------------
ffmpeg/ffprobe im Pfad. Kein numpy, kein PyYAML.

AUFRUFE
-------
    # Bericht: wo sind Pausen, wo darf geschnitten werden
    python3 pausen_scan.py --audio cut.mp4 --report

    # Gate: prüft die Schnitte aus dem Plan (Exit-Code 1 = nicht ausliefern)
    python3 pausen_scan.py --audio cut.mp4 --plan cut-plan.json

    # Gate mit Plosiv-Strenge (getrimmte Schnitte, siehe schnitt-regeln.md)
    python3 pausen_scan.py --audio cut.mp4 --plan cut-plan.json --vorlauf 0.25
"""

import argparse
import json
import re
import subprocess
import sys

# --- Regelwerte aus references/schnitt-regeln.md -----------------------------
# Segment-Einstieg 0,12-0,25 s VOR dem ersten Wort. 0,12 s ist das Minimum,
# 0,25 s die Pflicht bei getrimmten Schnitten (Plosive beginnen real bis 0,2 s
# vor dem Whisper-Onset).
VORLAUF_MIN_S = 0.12
VORLAUF_PLOSIV_S = 0.25
# Ausstieg ~0,15 s NACH dem letzten Wort.
NACHLAUF_MIN_S = 0.15
# Kürzer als das ist keine nutzbare Sprechpause, sondern eine Atempause im Wort.
PAUSE_MIN_S = 0.25


def ffmpeg_stderr(args):
    """Ruft ffmpeg auf und gibt stderr zurück. ffmpeg schreibt Filter-Ausgaben
    grundsätzlich nach stderr, auch im Erfolgsfall."""
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", *args],
        capture_output=True,
        text=True,
        errors="replace",
    )
    return proc.stderr


def messe_gating_schwelle(pfad):
    """Durchlauf 1: EBU-R128-Gating-Schwelle des Materials messen.

    Gibt (input_thresh, input_i) in dB zurück. Fällt auf einen konservativen
    Standardwert zurück, wenn loudnorm kein JSON liefert (z. B. bei sehr kurzem
    Material) — dann lieber eine unempfindliche Schwelle als ein Absturz."""
    stderr = ffmpeg_stderr(
        ["-i", pfad, "-map", "0:a:0", "-af", "loudnorm=print_format=json",
         "-f", "null", "-"]
    )
    treffer = re.search(r"\{[^{}]*\"input_thresh\"[^{}]*\}", stderr, re.S)
    if not treffer:
        return -45.0, None
    daten = json.loads(treffer.group(0))
    return float(daten["input_thresh"]), float(daten["input_i"])


def finde_pausen(pfad, schwelle_db, mindestdauer_s):
    """Durchlauf 2: Stillen mit adaptiver Schwelle finden.

    Gibt eine Liste von (start_s, ende_s) zurück, chronologisch."""
    stderr = ffmpeg_stderr(
        ["-i", pfad, "-map", "0:a:0",
         "-af", f"silencedetect=noise={schwelle_db:.2f}dB:d={mindestdauer_s}",
         "-f", "null", "-"]
    )
    starts = [float(m) for m in re.findall(r"silence_start:\s*(-?[\d.]+)", stderr)]
    enden = [float(m) for m in re.findall(r"silence_end:\s*([\d.]+)", stderr)]
    pausen = []
    for i, start in enumerate(starts):
        ende = enden[i] if i < len(enden) else None
        pausen.append((max(0.0, start), ende))
    return pausen


def hole_dauer(pfad):
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", pfad],
        capture_output=True, text=True,
    )
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return None


def baue_schnittfenster(pausen, dauer, vorlauf_s, nachlauf_s):
    """Wandelt Pausen in erlaubte Schnittfenster um.

    Ein Schnitt darf nicht direkt am Sprechbeginn kleben (Vorlauf) und nicht
    direkt am Sprechende (Nachlauf). Das Fenster ist die Pause abzüglich dieser
    Sicherheitsabstände. Pausen, die dadurch verschwinden, sind zu kurz zum
    Schneiden und fallen raus."""
    fenster = []
    for start, ende in pausen:
        ende_effektiv = ende if ende is not None else dauer
        if ende_effektiv is None:
            continue
        von = start + nachlauf_s
        bis = ende_effektiv - vorlauf_s
        if bis > von:
            fenster.append((von, bis, start, ende_effektiv))
    return fenster


def lade_geplante_schnitte(plan_pfad):
    """Liest die Schnittzeiten aus dem cut-plan.json.

    Berücksichtigt beide im Plan vorkommenden Quellen: die Liste `cuts` und die
    Segmentgrenzen unter `segments`, falls vorhanden."""
    with open(plan_pfad, encoding="utf-8") as f:
        plan = json.load(f)
    zeiten = []
    for wert in plan.get("cuts", []):
        zeiten.append(float(wert))
    for segment in plan.get("segments", []):
        for schluessel in ("in", "start", "t_in"):
            if schluessel in segment:
                zeiten.append(float(segment[schluessel]))
                break
    return sorted(set(round(z, 3) for z in zeiten))


def bewerte_schnitt(zeitpunkt, fenster):
    """Prüft einen Schnitt gegen die Fensterliste.

    Gibt (status, abstand_s, hinweis) zurück:
      'ok'      — liegt im erlaubten Fenster
      'knapp'   — liegt in einer Pause, aber innerhalb der Sicherheitszone
      'sprache' — liegt nicht in einer Pause
    """
    for von, bis, pause_start, pause_ende in fenster:
        if von <= zeitpunkt <= bis:
            return "ok", min(zeitpunkt - pause_start, pause_ende - zeitpunkt), ""
    for von, bis, pause_start, pause_ende in fenster:
        if pause_start <= zeitpunkt <= pause_ende:
            if zeitpunkt < von:
                return "knapp", von - zeitpunkt, "zu dicht am Sprechende davor"
            return "knapp", zeitpunkt - bis, "zu dicht am Sprechbeginn danach"
    return "sprache", 0.0, "kein Stille-Fenster an dieser Stelle"


def formatiere(sekunden):
    minuten = int(sekunden // 60)
    return f"{minuten:d}:{sekunden - minuten * 60:06.3f}"


def main():
    parser = argparse.ArgumentParser(
        description="Sprechpausen adaptiv finden und geplante Schnitte prüfen."
    )
    parser.add_argument("--audio", required=True,
                        help="Video- oder Audiodatei (die geschnittene Timeline)")
    parser.add_argument("--plan", help="cut-plan.json — aktiviert das Gate")
    parser.add_argument("--report", action="store_true",
                        help="Pausen und erlaubte Schnittfenster ausgeben")
    parser.add_argument("--vorlauf", type=float, default=VORLAUF_MIN_S,
                        help=f"Sicherheitsabstand vor dem Sprechbeginn in s "
                             f"(Standard {VORLAUF_MIN_S}, bei getrimmten "
                             f"Schnitten {VORLAUF_PLOSIV_S})")
    parser.add_argument("--nachlauf", type=float, default=NACHLAUF_MIN_S,
                        help=f"Sicherheitsabstand nach dem Sprechende in s "
                             f"(Standard {NACHLAUF_MIN_S})")
    parser.add_argument("--min-pause", type=float, default=PAUSE_MIN_S,
                        help=f"kürzeste als Pause gewertete Stille in s "
                             f"(Standard {PAUSE_MIN_S})")
    parser.add_argument("--schwelle", type=float,
                        help="Rauschschwelle in dB fest vorgeben statt messen "
                             "(nur für Sonderfälle)")
    args = parser.parse_args()

    dauer = hole_dauer(args.audio)

    if args.schwelle is not None:
        schwelle, integriert = args.schwelle, None
        quelle = "fest vorgegeben"
    else:
        schwelle, integriert = messe_gating_schwelle(args.audio)
        quelle = "gemessen (loudnorm input_thresh)"

    pausen = finde_pausen(args.audio, schwelle, args.min_pause)
    fenster = baue_schnittfenster(pausen, dauer, args.vorlauf, args.nachlauf)

    print(f"Datei      : {args.audio}")
    if dauer:
        print(f"Laufzeit   : {formatiere(dauer)}")
    if integriert is not None:
        print(f"Lautheit   : {integriert:.1f} LUFS")
    print(f"Schwelle   : {schwelle:.2f} dB ({quelle})")
    print(f"Pausen     : {len(pausen)} ab {args.min_pause} s")
    print(f"Schnittfenster: {len(fenster)} "
          f"(Vorlauf {args.vorlauf} s, Nachlauf {args.nachlauf} s)")

    if not pausen:
        print()
        print("WARNUNG: keine Pause gefunden. Entweder ist das Material "
              "durchgesprochen, oder die Audiospur ist nicht die erwartete. "
              "Vor dem Schneiden klären — nicht einfach weiterarbeiten.")

    if args.report:
        print()
        print("  #   Pause von      bis        Länge   Schnitt erlaubt von–bis")
        for i, (von, bis, p_start, p_ende) in enumerate(fenster, 1):
            print(f"  {i:<3} {formatiere(p_start):<14} {formatiere(p_ende):<10} "
                  f"{p_ende - p_start:5.2f}s  {formatiere(von)}–{formatiere(bis)}")

    if not args.plan:
        return 0

    schnitte = lade_geplante_schnitte(args.plan)
    if not schnitte:
        print()
        print("Kein Schnitt im Plan gefunden — nichts zu prüfen.")
        return 0

    print()
    print(f"Gate: {len(schnitte)} geplante Schnitte gegen die Pausen geprüft")
    print()
    verstoesse = 0
    warnungen = 0
    for zeitpunkt in schnitte:
        status, abstand, hinweis = bewerte_schnitt(zeitpunkt, fenster)
        if status == "ok":
            print(f"  OK      {formatiere(zeitpunkt)}  "
                  f"(Abstand zur Sprache {abstand:.2f} s)")
        elif status == "knapp":
            warnungen += 1
            print(f"  KNAPP   {formatiere(zeitpunkt)}  "
                  f"{abstand:.2f} s zu wenig — {hinweis}")
        else:
            verstoesse += 1
            print(f"  SPRACHE {formatiere(zeitpunkt)}  {hinweis}")

    print()
    if verstoesse:
        print(f"DURCHGEFALLEN: {verstoesse} Schnitt(e) liegen auf Sprache. "
              f"Silben werden verschluckt — Schnittpunkt in die nächste Pause "
              f"verschieben, nicht nachträglich ausblenden.")
        return 1
    if warnungen:
        print(f"DURCHGEFALLEN: {warnungen} Schnitt(e) kleben am Sprechrand. "
              f"Bei Plosiven (D, Z, K, B) hörbar. Schnittpunkt in die Mitte der "
              f"Pause legen.")
        return 1
    print("BESTANDEN: alle Schnitte liegen sauber in Sprechpausen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
