# Ton-Pipeline

Der Ton entscheidet, ob ein Schnitt professionell wirkt. Jede Regel hier stammt aus einem real aufgetretenen, hörbaren Fehler.

## Segment-Ebene

- **8-ms-Fade an JEDER Segment-Audio-Kante** (`afade=t=in:d=0.008` + `afade=t=out`): unhörbar, killt jeden Klick. Harter Audio-Concat ohne Fades erzeugt Wellenform-Sprünge (Klack).
- Sprach-Normalisierung pro Segment nur statisch: Quellfenster mit `ebur128` messen, `volume=(Ziel − I) dB` setzen. **`loudnorm` regelt bei Segmenten < 3–4 s faktisch nicht** (braucht ~3 s Vorlauf).

## Master-Kette (auf der fertigen Timeline)

1. Audio **NIE aus dem Segment-Concat ziehen** (siehe „AAC-Priming-Drift" unten): jedes Segment einzeln zu WAV dekodieren, mit atrim/apad exakt auf die Container-Dauer (`ffprobe format=duration`) bringen, per concat-FILTER zu PCM zusammensetzen → Audiolänge == Video-Timeline.
2. `highpass=85 Hz` → `acompressor` 2:1 (threshold −24 dB, attack 6, release 250, soft knee) — glättet Pegelsprünge zwischen Clips natürlicher als loudnorm allein.
3. SFX-Spur dazumischen (`amix duration=first, normalize=0`), ~18 dB unter Sprache.
4. **Linear normalisieren statt dynamisch:** Mix als WAV, `ebur128` messen, `volume=(−14 − I) dB` + `alimiter=limit=0.81:level=false`. Ziel: −14 LUFS ±0,5, True Peak ≤ −1,2 dB. Bei kleiner LRA (< 6) klingt linear ohnehin besser (kein Pumpen).
5. Unter das Concat-Video muxen: `-map 0:v -c:v copy`.

## SFX (selbst synthetisiert, lizenzfrei, reproduzierbar)

- **Pop** = 90 ms Sinus-Pitch-Drop 500→130 Hz · **Boom** = 350–500 ms Sinus 120→48 Hz · **Whoosh** = ~340 ms Bandpass-Noise-Sweep mit Sinus-Hüllkurve.
- Als EINE timeline-lange Mono-WAV aus einer `events.json` gebaut (Events = Typ + Zeit), Ziel-Peak ≈ −12 dB.
- Platzierung: Pop auf jedes Emphasis-Landing (+0,04 s nach Animations-Onset), Boom nur auf den größten Zahlen-Moment, Whoosh auf Snap-Transitions (läuft auf den Schnitt zu, Start ≈ 0,17 s davor). Nicht mehr — Zurückhaltung ist der Unterschied zu Spam-Content.
- **Bei jeder Timing-Änderung die SFX-Spur mit regenerieren** und die Event-Zeiten maschinell gegen die Overlay-Enable-Zeiten im Render-Skript prüfen. Keine hartkodierten Zeiten in der Event-Generierung — immer aus den Emphasis-Definitionen ableiten.

## Pausen adaptiv messen (statt mit fester Schwelle)

Sprechpausen sind die Grundlage von zwei Dingen: der wichtigsten Schnittregel
(„Schnitte in die Pause") und der Karten-Logik (Pause > 0,6 s bricht die Karte).
Beide waren bis v0.8 auf eine feste Rauschschwelle angewiesen — und die ist bei
leisem Material blind und bei lautem überempfindlich.

**Richtig ist ein zweistufiges Verfahren:**

```bash
# 1 · Gating-Schwelle DES MATERIALS messen
ffmpeg -i cut.mp4 -map 0:a -af loudnorm=print_format=json -f null -
#    -> input_i      = integrierte Lautheit
#    -> input_thresh = EBU-R128-Gating-Schwelle  <- das ist der gesuchte Wert

# 2 · Stille mit genau dieser Schwelle suchen
ffmpeg -i cut.mp4 -map 0:a -af "silencedetect=noise=${THRESH}dB:d=0.25" -f null -
```

`d=0.25` ist die Untergrenze einer nutzbaren Sprechpause — kürzeres ist eine
Atempause innerhalb des Wortflusses und kein Schnittpunkt.

Beides zusammen macht `scripts/pausen_scan.py`, inklusive der Umrechnung in
erlaubte Schnittfenster (Pause minus Vor- und Nachlauf) und dem Gate gegen den
`cut-plan.json`. **Findet der Scan keine einzige Pause, ist das kein Ergebnis,
sondern ein Alarm** — meist ist die falsche Audiospur gemappt.

## Bekannte Fallen (Pflichtwissen)

- **AAC-Priming-Drift:** mp4/AAC-Segmente + concat-Demuxer → jede Segmentgrenze injiziert ~12–27 ms Stille, sobald ffmpeg das Audio DEKODIERT. Player spielen die Concat-Datei korrekt, aber jede Master-Stufe backt den Drift ein (kumulativ 0,5–0,8 s pro 100 s → Untertitel wirken ab der Mitte asynchron). Fix: siehe Master-Kette Schritt 1. Verifikation: silencedetect-Pausenpositionen Concat vs. Final müssen auf ±30 ms übereinstimmen.
- **`loudnorm` nach `amix` streckt Audio** (One-Pass-Modus, interne 192-kHz-Timestamps): Ergebnis war +0,8 s Länge und wandernder Sync. Deshalb linear mastern (oben Schritt 4).
- **Whisper-Onsets:** nach Pausen/Schnitten oft 0,2–0,3 s zu FRÜH, bei Plosiven bis 0,2 s zu SPÄT, einzelne Wörter bis 0,5 s verschoben. Bei jedem gemeldeten Sync-Problem die RMS-Hüllkurve messen statt Whisper zu glauben (Onset-Audit in `render-technik.md`).
- Video- vs. Audio-Streamdauer der Lieferdatei > 0,1 s auseinander = Alarm, nicht liefern.

## Fremdmaterial im Mix (Reaction-/Quellclips)

- **Pro Quelle messen, dann angleichen:** Fremd-Quellclip und eigener Sprecher liegen real oft
  10+ dB auseinander (gemessen: Quellclip −16,2 LUFS, Sprecher −26/−27 LUFS — ungeglichen wäre
  der eigene Mann die leiseste Stimme im eigenen Video). Deshalb VOR dem Master jedes Segment
  mit ebur128 messen und per Segment-Gain auf eine gemeinsame Sprach-Lautheit bringen
  (Differenz danach ≤ 2 dB), erst dann die Master-Kette fahren.

## Kunden-SFX-Dateien (Pflicht-Vermessung)

- Gelieferte SFX-Dateien nie blind nutzen: Dateilänge ≠ hörbare Länge. Realfall: 1,09-s-Datei,
  hörbar nur die ersten 0,22 s (Peak bei 0,18 s, Rest Stille) — wer die Datei am Schnitt ENDEN
  lässt, setzt den Peak 0,87 s zu früh.
- Vorgehen: Hüllkurve messen, Stille wegschneiden, Datei auf den hörbaren Kern kürzen und den
  PEAK auf das Ziel-Event legen (bei Whoosh: Peak auf den Schnitt, Start entsprechend davor).
  Nach dem Render maschinell gegenprüfen (Soll-Event vs. gemessener Peak ≤ 40 ms).
