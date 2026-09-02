# Untertitel-System — Karaoke + Emphasis

Ein System, zwei Beats: `karaoke` (der ruhige Grundtakt, 80–90 % des Videos) und `emphasis` (der Punch). Wenn alles animiert, wirkt nichts — die Wirkung entsteht aus dem Kontrast.

Alle Farben/Fonts/Positionen kommen aus der `kunden-config.yaml`. Nie hart kodieren.

## Presets

### 1 · `karaoke` — Standard-Zeile
Wort-für-Wort-Highlight: weiße Zeile (Standard-Font Bold), aktuelles Wort auf Akzent-Chip (abgerundetes Rechteck). Max. 4 Wörter / ~26–30 Zeichen pro Zeile, Umbruch bevorzugt an Satzzeichen, zusammengesetzte Wörter nie trennen. Weicher Schatten (Gaussian Blur) hinter der Zeile für Lesbarkeit auf jedem Hintergrund.

**Timing-Regeln (alle sind Pflicht, jede hat einen sichtbaren Fehler verhindert):**
- Wort-Timings aus Whisper (`word_timestamps=True`), danach Nachbearbeitung: Bindestrich-Tokens zum Vorgänger mergen; Onset-Audit gegen die RMS-Hüllkurve (siehe `render-technik.md`).
- **Anzeige-Vorlauf 0,10 s** vor dem Wort-Onset (früh wirkt synchron, spät wirkt falsch); in schnellen Passagen bis 0,25 s. Der Vorlauf gilt NUR für die Anzeige — Rohzeiten bleiben die Referenz für Segment-Zuordnung und Emphasis-Fenster.
- **Zeilenwechsel exakt und lückenlos:** Ende der letzten Zeile == Anzeige-Start der nächsten Zeile. Kurze Lücken < 0,25 s zwischen Zeilen auffüllen (kein Flackern); nur bei echten Sprechpausen ≥ 0,25 s darf der Untertitel verschwinden. Letztes Wort einer Zeile: Highlight-Tail max. +0,15 s.
- Overlay-Fenster als **halboffene Intervalle** (`gte(t,a)*lt(t,b)`) — inklusives `between()` erzeugt an Grenz-Frames Doppel-Highlights oder braucht künstliche Lücken (= Leerframes, sichtbares Springen).
- Fenster kürzer als 0,02 s nicht emittieren.

### 2 · `emphasis` — der Highlight-Beat
Ersetzt die Karaoke-Zeile (nie beides gleichzeitig, nie denselben Text doppelt). 1–3 Wörter, Versalien, schwerster Font-Schnitt. Vier Ebenen, framegenau synchron:
1. **Snap-Pop**: 0→100 % in 0,2 s, Ease-Out-Back (Overshoot ~8 %), erste 2 Frames Motion-Blur, Land-Jitter ±3 px (2 Frames).
2. **Punch im Video**: Emphasis-Start ist immer ein Schnitt mit Zoomstufen-Wechsel (+8–15 %).
3. **Keyword-Glow**: weicher Akzent-Puls hinter genau EINEM Keyword (0,35 s Sinus).
4. **Micro-Drift**: +1,8 % Scale über die Haltezeit; Exit: Whip-down + Fade 0,15 s.
Optional gestaffelte Unterzeile (Sub-Font, +0,35 s versetzt). SFX: Pop auf das Landing (+0,04 s).

**Die Kurven dieser vier Ebenen stehen als Zahlen in `animation-kurven.md`** —
Overshoot 8,0 % ist `cubic-bezier(0.34, 1.50, 0.64, 1)`, der Peak liegt bei 59 %
der Animationsdauer (also 0,118 s bei 0,20 s Dauer), und dort setzt der
SFX-Versatz von 0,04 s an. „Ease-Out-Back mit ungefähr 8 %" ist keine prüfbare
Angabe; die Tabelle dort ist es.

*Bewusst gestrichen: Underline-Sweep — wirkte in der Praxis unruhig. Nicht wieder einführen.*

### 3 · `list-build` — Aufzählungs-Aufbau
Für Formeln/Aufzählungen („Was? / Für wen? / Mit welchem Nutzen?"): Zeilen poppen nacheinander exakt auf den Sprech-Beat (echte Onsets, nicht Whisper blind glauben), gelandete Zeilen bleiben stehen. Jede Zeile = Mini-`emphasis` ohne Glow.

### 4 · `number-slam` — Zahlen
`emphasis`-Variante: Die Zahl ist immer das Keyword (Akzentfarbe), Rest weiß. Konkrete Zahl schlägt runde Formulierung. Der größte Zahlen-Moment des Videos bekommt zusätzlich den Boom-SFX.

### 5 · `cta-arrow` — Abschluss-CTA
`emphasis` + bounzender Richtungspfeil (Sinus-Loop 0,6 s) Richtung Formular/Swipe. Letzte 3–5 s.

### 6 · `quiet` — B2B-/Ruhig-Modus
Weiße Zeile ohne Chip, nur das aktuelle Wort in Akzentfarbe. Für Intensität „ruhig".

### 7 · `badge` — Top-Badge
Uppercase-Badge in Akzentfarbe im oberen Drittel für Datum/Label — nur wenn die untere Zone belegt ist, nie gleichzeitig mit `emphasis`.

## Verbindliche Regeln

- Emphasis-Dichte: **max. 3 High-Impact-Momente pro Minute**, dazwischen 6–8 s ruhiges Material. Intervalle variieren (3 s / 5 s / 2,5 s), nie exakt getaktet.
- Caption-Text = exakt das Gesprochene. Kürzen erlaubt, erfinden nie.
- Position: 16:9 → unteres Drittel (y ≈ 86 % der Höhe als Zeilenmitte); 9:16 → 62–70 % („Hormozi-Zone"), nie über dem Mund. Plattform-UI-Zonen (9:16: oben 250 px, unten 400 px) meiden.
- Immer dieselbe Akzentfarbe für Chip, Keyword, Glow, CTA.
- Wörter, die in ein Emphasis-Fenster fallen (±0,35 s Marge), bekommen KEINE Karaoke-Zeile.

## Transitions-Baukasten

- **Standard: harter Cut + Zoomstufen-Wechsel** (100 ↔ 112 ↔ 125 %) an Satzgrenzen alle 3–5 s.
- **Snap-Transition** (0,15–0,2 s, hohe Beschleunigung): nur an den 2–3 größten Erzähl-Nahtstellen (Reveal, Kapitelwechsel, CTA). `xfade=zoomin` ab ffmpeg 5.x, sonst `hblur`.
- **Speed-Ramp** auf Action-Peaks (nur 60-fps-Material, 0,5× ab exakt dem Peak).
- **Weiß-/CI-Blitz** (0,1 s fade-in from color) an Kapitelanfängen — sparsam.
- Keine Spins, Wipes, Slides in Business-Content.
- SFX-Paarung: Cut/Zoom → Whoosh, Text → Pop, Reveal/große Zahl → Boom. Framegenau (Details in `audio.md`).

## Vermessener Referenz-Standard (Pflichtwerte)

Diese Werte stammen aus der Vermessung eines abgenommenen Referenz-Schnitts und sind der
Default für jede Karaoke-Zeile (Farben kommen weiter aus der Kunden-Config):

| Eigenschaft | Wert |
|---|---|
| Schriftschnitt | der SCHWERSTE verfügbare Schnitt (ExtraBold/Black), nie Bold wenn schwerer existiert |
| Textfarbe | Off-White `#F0F0F0` (nie reines Weiß) |
| Kontur | KEINE (max. 1 px, nur wenn Kunden-CI es verlangt) |
| Schatten | Gaussian Blur 7, Alpha 0,72, Offset dy 4 — deutlich sichtbar |
| Chip (aktives Wort) | Padding 13/7 px, Radius 11, exakt auf der Ink-Box |
| Wörter pro Karte | max. 3 |
| Zeilenbreite | max. 860 px im 1080er-Raster — nie fast volle Bildbreite |

**Chip-Ausrichtung: Ink-Box, nicht Ascender-Box.** Die Ascender-Box enthält Leerraum über den
Versalien — daran ausgerichtet sitzt der Chip systematisch zu hoch und die Schrift wirkt nicht mittig.
Ink-Box einmal mit Referenzstring („Hg“) messen und für ALLE Wörter identisch verwenden,
sonst springen die Chips beim Wortwechsel.

**Gemessen wird mit exakt denselben Textparametern wie gerendert** — inklusive
`letterSpacing` bzw. Laufweite. Wird beim Messen ein Parameter weggelassen, der
beim Rendern gesetzt ist, stimmt jede Chip-Breite systematisch nicht, und kein
Timing-Gate schlägt an. Praktisch heißt das: ein Stil-Objekt definieren und
sowohl an die Messung als auch an das Zeichnen übergeben, nie zwei Parametersätze
pflegen.

**Und: prüfen, dass der Kunden-Font wirklich geladen ist.** Fällt die
Schriftauflösung still auf einen Ersatz-Font zurück, wird gegen falsche Metriken
gemessen — das Ergebnis sieht „fast richtig" aus und ist es nirgends. Der
Ladefehler muss laut scheitern, nicht stillschweigend ersetzen.

## Kontrast-Gate (Pflicht vor jedem Render)

Der häufigste Totalschaden: helle Untertitel auf hellem Hintergrund (weißes Hemd, helle Wand)
— das Video besteht jedes Timing-QC und ist trotzdem unlesbar. Deshalb:

1. **Messen:** Für jede Untertitel-Karte einen Frame an der Kartenmitte ziehen und die mittlere
   Luminanz des Text-Bereichs messen (`crop` auf die Textzone + `signalstats` YAVG).
2. **Bewerten:** YAVG > 140 in der Textzone = heller Hintergrund = weiße Schrift ohne
   Gegenmaßnahme verboten.
3. **Gegenmaßnahmen-Leiter (in dieser Reihenfolge):**
   a) **Position innerhalb der erlaubten Zone verschieben** — die dunkelste stabile Teilzone wählen
      (z. B. tiefer, wenn unten dunkler Boden/Kleidung ist).
   b) **Ganzzeilen-Scrim:** dunkler halbtransparenter Chip hinter der GESAMTEN Zeile
      (Schwarz, Alpha 0,35–0,5, gleiche Radius-Logik wie der Wort-Chip) — nicht nur hinter dem Emphasis-Wort.
   c) Schatten verstärken (Blur 9–10, Alpha 0,85) — nur als Ergänzung, ersetzt a/b nicht.
4. **Konstanz:** Die gewählte Lösung gilt für das GANZE Video — Position und Stil der Zeile
   springen nicht von Karte zu Karte.

## Kollisions-Regeln (Pflicht)

- Untertitel liegen NIE über: Gesicht/Mund, Händen mit Objekten, eingeblendeten Logos oder
  Schrift IM Bild (z. B. Logo auf dem Polo-Shirt!), Plattform-UI-Zonen.
- Vor dem Render 3 Frames (Anfang/Mitte/Ende) prüfen: kollidiert die Textzone mit einem dieser
  Elemente, Position innerhalb der erlaubten Zone anpassen — einmal, für das ganze Video.
- Hook-Overlays: siehe `hooks.md` — gleiche Typografie wie die Untertitel, eigene Positionsregeln.

## Vollständigkeits-Regel (Pflicht)

Die Emphasis-Unterdrückung („Wörter im Emphasis-Fenster bekommen keine Karaoke-Zeile“)
arbeitet auf WORT-Ebene, nie auf Karten-Ebene — sonst verschwinden ganze Halbsätze aus den
Untertiteln. Abschluss-Check vor Lieferung: jedes gesprochene Wort des Transkripts erscheint entweder
in einer Karaoke-Karte oder in einem Emphasis-Overlay. Fehlende Wörter = nicht liefern.
