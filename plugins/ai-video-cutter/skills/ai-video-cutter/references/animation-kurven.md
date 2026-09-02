# Animations-Kurven und Frame-Mathematik

Bis v0.7 standen die Kurven als Prosa in `captions.md` („Ease-Out-Back, Overshoot
~8 %"). Prosa lässt sich nicht prüfen — zwei Builds mit derselben Beschreibung
sahen unterschiedlich aus, und niemand konnte sagen, welcher richtig war. Hier
stehen die Zahlen.

---

## 1 · Die Kurven-Tabelle

Alle Kurven als CSS-`cubic-bezier(x1, y1, x2, y2)` notiert. Das ist die
Austauschwährung: Python wertet sie mit der Formel unten aus, jedes Design-Tool
versteht dieselbe Schreibweise, und der Wert ist damit zwischen Plan, Generator
und Gestaltung eindeutig.

| Einsatz | Kurve | Charakter |
|---|---|---|
| **Snap-Pop** (Emphasis-Einsatz) | `cubic-bezier(0.34, 1.50, 0.64, 1)` | Overshoot **8,0 %** |
| Snap-Pop, kräftiger | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Overshoot 9,8 % (Standard-easeOutBack) |
| **Push-in / Zoomfahrt** | `cubic-bezier(0.16, 1, 0.3, 1)` | easeOutExpo — schnell an, weich aus, kein Überschwingen |
| **Exit / Whip-down** | `cubic-bezier(0.7, 0, 0.84, 0)` | easeInExpo — beschleunigt weg |
| Micro-Drift (Haltezeit) | `linear` | darf nicht „arbeiten" |
| Sinus-Puls (Glow, CTA-Pfeil) | `sin(2π · t / periode)` | kein Bezier — echte Sinusfunktion |

**Overshoot exakt einstellen.** Nur `y1` steuert den Overshoot, gemessen an
`cubic-bezier(0.34, y1, 0.64, 1)`:

| y1 | 1.20 | 1.30 | 1.40 | 1.45 | **1.50** | 1.56 | 1.60 | 1.70 | 1.80 |
|---|---|---|---|---|---|---|---|---|---|
| Overshoot | 1,3 % | 3,0 % | 5,3 % | 6,6 % | **8,0 %** | 9,8 % | 11,0 % | 14,3 % | 17,7 % |

Über 12 % wirkt der Pop nach Cartoon, nicht nach Creator. Bei B2B-Kunden
(Intensität „ruhig") 1.30–1.40 verwenden.

**Auswertung in Python** — identisch zur CSS-Semantik, damit Plan und Render
dieselbe Kurve meinen:

```python
def bezier_komponente(t, a, b):
    mt = 1 - t
    return 3 * mt * mt * t * a + 3 * mt * t * t * b + t * t * t

def bezier_y(x, x1, y1, x2, y2, iterationen=40):
    """y-Wert der CSS-Kurve an der Stelle x (0..1). Binäre Suche über den
    Parameter, weil x(t) nicht analytisch invertierbar ist."""
    lo, hi = 0.0, 1.0
    for _ in range(iterationen):
        mitte = (lo + hi) / 2
        if bezier_komponente(mitte, x1, x2) < x:
            lo = mitte
        else:
            hi = mitte
    return bezier_komponente((lo + hi) / 2, y1, y2)
```

---

## 2 · Skalierung wahrnehmungsgerecht interpolieren

**Die Falle:** Eine linear interpolierte Skalierung wirkt nicht linear. Je größer
der Zoom schon ist, desto kleiner wirkt derselbe absolute Zuwachs — die Fahrt
scheint auszubremsen, obwohl die Zahlen gleichmäßig steigen. Der Grund ist
wahrnehmungspsychologisch: Größenunterschiede werden relativ empfunden, nicht
absolut (Weber-Fechner). Wer linear interpoliert, baut deshalb systematisch eine
Fahrt, die hinten zäh wird.

**Die Korrektur** ist geometrische statt arithmetischer Interpolation:

```python
def scale_wahrnehmung(t, von, bis):
    """t in 0..1. Gleichmäßig WAHRGENOMMENE Zoomfahrt von 'von' nach 'bis'."""
    return von * (bis / von) ** t

# Gegenprobe bei einem Push-in 100 % -> 125 %:
#   linear      bei t=0,5 -> 112,50 %
#   wahrnehmung bei t=0,5 -> 111,80 %
```

Der Unterschied ist klein und trotzdem sichtbar, weil er über die ganze Fahrt
ungleich verteilt ist. **Anwenden auf:** Push-in bei Standbildern (8–12 %),
Micro-Drift (+1,8 %), Punch-Zoom beim Emphasis-Einsatz, Ken-Burns-Fahrten.

**Nicht anwenden auf die Zoomstufen selbst.** Nachgerechnet: 100 → 112 → 125 hat
die Verhältnisse 1,120 und 1,116, geometrisch exakt wären 111,80 statt 112. Die
Abweichung ist 0,2 % und damit unsichtbar. **Die bestehenden Zoomstufen sind
richtig und bleiben, wie sie sind** — die Korrektur betrifft ausschließlich
*animierte* Fahrten über die Zeit, nicht die harten Stufenwechsel.

---

## 3 · Frame-Mathematik

Alles Sichtbare passiert auf Frames, nicht auf Sekunden. Sekunden sind die
Schreibweise im Plan, Frames sind die Wahrheit im Bild.

**Umrechnung, verbindlich:**

```
frame  = round(sekunden * fps)
sekunde = frame / fps
```

Frame 0 ist der Zeitpunkt 0,000 s. Ein Clip mit `n` Frames hat die Frames
`0 … n-1` — **der letzte Frame ist `n-1`, nicht `n`.**

**Die Off-by-one-Falle beim Animationsfortschritt.** Der Fortschritt einer
Animation über `n` Frames wird gegen `n-1` normalisiert:

```python
fortschritt = min(1.0, max(0.0, frame / (dauer_frames - 1)))
```

Gegen `dauer_frames` normalisiert erreicht die Animation nie 1,0 — der Snap-Pop
landet dann dauerhaft 1–2 % unter seiner Zielgröße, der Micro-Drift startet vom
falschen Wert, und das Ganze sieht „irgendwie weich" aus, ohne dass ein Gate
anschlägt. Das ist die stille Variante des Fehlers.

**Rundungstabelle für die Standardwerte des Systems:**

| Dauer | 24 fps | 25 fps | 30 fps | 50 fps | 60 fps |
|---|---|---|---|---|---|
| Snap-Pop 0,20 s | 5 | 5 | 6 | 10 | 12 |
| Exit-Fade 0,15 s | 4 (3,60) | 4 (3,75) | **4 (4,50)** | 8 (7,50) | 9 |
| Anzeige-Vorlauf 0,10 s | 2 (2,40) | 3 (2,50) | 3 | 5 | 6 |
| SFX-Versatz 0,04 s | 1 (0,96) | 1 | 1 (1,20) | 2 | 2 (2,40) |

Fett markiert der unangenehmste Fall: 0,15 s bei 30 fps sind 4,5 Frames. Immer
`round()` verwenden — nie mal ab-, mal aufrunden. **Dauern, die Material
enthalten müssen** (Segmentlängen, Kompositionsdauer), werden dagegen mit
`ceil()` aufgerundet, sonst fehlt am Ende ein halber Frame Bild.

**Nie Frame-Konstanten in Regeln schreiben.** Eine Transition ist „0,18 s", nicht
„6 Frames" — sonst dauert sie bei einem 60-fps-Kunden die Hälfte. Alle Zeitwerte
im `cut-plan.json` stehen in Sekunden; Frames entstehen erst im Generator, aus
der tatsächlichen fps des Materials.

---

## 4 · Der Emphasis-Beat, vollständig in Zahlen

Die vier Ebenen aus `captions.md`, jetzt mit Kurve und Frame-Bezug. Alle vier
starten auf demselben Frame — das ist der ganze Trick.

| Ebene | Dauer | Kurve | Werte |
|---|---|---|---|
| Snap-Pop (Scale) | 0,20 s | `cubic-bezier(0.34, 1.50, 0.64, 1)` | 0 → 1,0 mit 8 % Overshoot |
| Motion-Blur | erste 2 Frames | — | nur solange die Kurve > 1,0 steigt |
| Land-Jitter | 2 Frames nach Peak | — | ±3 px, dann exakt 0 |
| Punch-Zoom im Video | auf dem Startframe | hart | +8–15 %, kein Übergang |
| Keyword-Glow | 0,35 s | Sinus, eine Halbwelle | Alpha 0 → max → 0 |
| Micro-Drift | Haltezeit | linear, `scale_wahrnehmung` | +1,8 % gesamt |
| Exit | 0,15 s | `cubic-bezier(0.7, 0, 0.84, 0)` | Whip-down + Fade auf 0 |
| SFX-Pop | Peak + 0,04 s | — | nicht auf den Start, auf das Landing |

**Der Pop sitzt auf dem Landing, nicht auf dem Einsatz.** Nachgerechnet an der
Kurve: der Peak von `cubic-bezier(0.34, 1.50, 0.64, 1)` liegt bei **59,0 % der
Animationsdauer**, bei 0,20 s Gesamtdauer also **0,118 s nach dem Start**. Der
SFX-Pop gehört auf Peak + 0,04 s, das sind 0,158 s nach dem Animationsstart. Wer
den Pop auf den Startframe legt, hört ihn 0,16 s vor dem Bild — hörbar daneben.

(Zum Vergleich, falls jemand die kräftigere Kurve wählt: `y1 = 1.56` hat ihren
Peak bei 57,3 % der Dauer, also 0,115 s.)

---

## 5 · Die sechs verbindlichen Werte

Diese Werte sind der Vertrag zwischen Schnittplan und Render. Sie stehen nicht
zur Diskussion und werden nicht pro Video neu entschieden:

1. Overshoot des Snap-Pop: **8,0 %** (`y1 = 1.50`)
2. Snap-Pop-Dauer: **0,20 s**, Exit **0,15 s**
3. Anzeige-Vorlauf der Karaoke-Zeile: **0,10 s** (schnelle Passagen bis 0,25 s)
4. SFX-Pop: **Peak + 0,04 s**
5. Zoomstufen: **100 / 112 / 125 %**, harte Wechsel
6. Emphasis-Dichte: **max. 3 pro Minute**

Diese sechs Werte gehören ins Standards-Echo, bevor gebaut wird. Abweichungen
sind Kunden-Learnings und gehören in `kunden-learnings.md` oder die Config — nie
in einen Einzelfall-Beschluss während des Builds.
