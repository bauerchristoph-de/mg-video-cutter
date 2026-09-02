# scripts/ — die ausführbare Hälfte des Video-Cutters

Alles, was bei **jedem** Video gleich ist, liegt hier als Code. Video-spezifisch
bleibt nur der `cut-plan.json`. Vorher wurde die Untertitel-Erzeugung pro Video
neu geschrieben — mit der Folge, dass dieselben Fehler mehrfach auftraten
(Chip an der falschen Box, verschluckte Wörter, unlesbare Zeilen auf hellem Grund).

**Regel: Diese Skripte werden benutzt, nicht nachgebaut.** Wenn etwas fehlt,
gehört es hier hinein und ins nächste Release — nicht in den Projektordner.

## Ablauf

```bash
# 0a · VOR dem Schnittplan: wo darf überhaupt geschnitten werden
python3 pausen_scan.py --audio cut.mp4 --report

# 0b · NACH dem Schnittplan: liegt ein geplanter Schnitt auf Sprache?
python3 pausen_scan.py --audio cut.mp4 --plan cut-plan.json

# 1 · Kontrast messen und Scrim-Entscheidung in den Plan schreiben
python3 contrast_probe.py --video cut.mp4 --plan cut-plan.json --apply

# 2 · Overlays + SFX-Events bauen
python3 build.py --config kunden-config.yaml --plan cut-plan.json --out build/

# 3 · SFX-Spur erzeugen (Peaks werden gegen die Events gemessen)
python3 make_sfx.py --events build/events.json --duration 35.3 --out build/sfx.wav --check

# 4 · Overlay + Ton auf das Video legen (ffmpeg, video-spezifisch)
ffmpeg -i cut.mp4 -framerate 30 -i build/ovl/f%05d.png \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto" ... final.mp4

# 5 · Pflicht-QC — Exit-Code 1 heißt: nicht ausliefern
python3 qc.py --video final.mp4 --build build/ --plan cut-plan.json
```

## cut-plan.json — das einzige, was pro Video geschrieben wird

```json
{
  "timeline": { "end": 35.3 },
  "words": [ { "w": "Wir", "s": 3.10, "e": 3.42 } ],
  "hook": {
    "lines": [["WANN","SOLLTEST","DU"],["DIE","SECURITY","HOLEN?"]],
    "keyword": "SECURITY", "y": 712, "in": 0.18, "until": 9.47
  },
  "emphasis": {
    "onset": 19.56, "hold_end": 20.84, "end": 20.99,
    "lines": [["LIEBER","EINMAL"],["ZU","VIEL"]], "keyword": "EINMAL"
  },
  "cuts": [9.47, 22.75],
  "boom": [],
  "style": { "karaoke": { "scrim": { "alpha": 0.45 } } }
}
```

* `words` — Wort-Timings **nach** Onset-Audit und Segment-Remap (nicht roh aus Whisper).
* `hook.until` — bis wann der Hook steht (danach greifen die Karaoke-Karten).
* `emphasis.lines` — was die Emphasis anzeigt. Nur diese Wörter werden aus den
  Karaoke-Karten entfernt; alles andere im Zeitfenster bleibt sichtbar.
* `cuts` — die Schnittzeitpunkte. Werden von `pausen_scan.py --plan` gegen die
  gemessenen Sprechpausen geprüft.
* `style` — optionale Überschreibungen nur für dieses Video. Der Normalfall ist,
  hier nichts zu setzen: Der Stil kommt aus der Kunden-Config.

## Was die Skripte selbst absichern

| Prüfung | Wo | Verhindert |
|---|---|---|
| Schnitt liegt in einer Sprechpause | `pausen_scan.py --plan` | verschluckte Silben („Zweitens" → „weitens") |
| Chip auf der Ink-Box | `build.py` | Chip sitzt zu hoch, Schrift wirkt nicht mittig |
| Wort-Ebene statt Karten-Ebene bei Emphasis | `build.py` | verschwundene Halbsätze |
| Sprechpause > 0,6 s bricht die Karte | `build.py` | Wörter aus zwei Sinneinheiten in einer Karte |
| kein Wort fällt aus den Karten | `build.py` (assert) | stille Textverluste |
| Luminanz der Textzone | `contrast_probe.py` | unlesbare Schrift auf hellem Grund |
| Peak-Lage der SFX | `make_sfx.py --check` | Effekt liegt hörbar neben dem Schnitt |
| 8 Gates + Kontaktbogen | `qc.py` | Auslieferung mit erkennbarem Fehler |

## Abhängigkeiten

`pillow`, `pyyaml`, `ffmpeg`/`ffprobe` im Pfad.
Fehlt PyYAML: `pip install pyyaml --break-system-packages`
`pausen_scan.py` braucht nur ffmpeg/ffprobe — kein numpy, kein PyYAML.

## Performance

`build.py` dedupliziert identische Frames (bei Karaoke ändert sich nur alle
~9 Frames etwas) und hardlinkt sie. Gemessen an einem 11,5-s-Testvideo:
344 Frames, davon 84 gerendert — **76 % gespart**, ~13 s Laufzeit bei 1080×1920.

`pausen_scan.py` lässt die Arbeit über die Videolänge in ffmpeg laufen und sieht
in Python nur die Ereignisliste (typisch 10–200 Pausen). Bei 10× längerem
Material wächst nur die ffmpeg-Zeit linear.
