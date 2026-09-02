# Render-Technik & QC

Architektur für reproduzierbare, resumable Renders mit ffmpeg — entstanden aus zwei Produktionen (9:16-Projektfilm, 16:9-Webinar-Cut) und deren sämtlichen Fehlschlägen.

## Architektur

**Ein Python-Generator ist die einzige Quelle der Wahrheit.** Er hält den Schnittplan (SEGS: Name, Quell-In/Out, Zoomstufe), die Emphasis-Definitionen und die Wort-Timings — und erzeugt daraus ALLE Artefakte: Untertitel-PNGs (PIL), Emphasis-PNG-Sequenzen (Ease-Kurven, Glow, Motion-Blur in Python vorgerendert — nicht als ffmpeg-Expressions), `events.json` (SFX), SFX-WAV und das Render-Skript. Niemals einzelne Werte im generierten Skript von Hand patchen.

- **Jede programmatische Änderung am Generator mit `assert`** (Ersetzungs-Pattern muss exakt treffen), danach das generierte Skript maschinell gegenprüfen (greps auf die erwarteten Werte). Stille sed/replace-Fehlschläge haben zweimal ganze Feedbackrunden gekostet.
- Ein Render-Segment pro ffmpeg-Aufruf: Quelle trimmen → Video-Kette (fps, crop/scale für Zoomstufe, `setsar=1`, Grade) → Overlays → Audio mit Kanten-Fades. Overlay-Enables für Standbild-PNGs **halboffen** (`gte(t,a)*lt(t,b)`); PNG-Sequenzen mit `setpts=PTS-STARTPTS+offset/TB`.
- **Atomic Writes:** immer nach `tmp.mp4` rendern und erst nach Erfolg `mv` — ein gekillter Render hinterlässt sonst eine gekürzte Datei, die Dauer-Checks bestehen kann.
- Resumable: `ok()`-Check pro Segment (existiert + Video≈Audio-Dauer, |v−a| < 0,15 s), Zeitbudget pro Aufruf, Skript so oft aufrufen bis alles fertig ist. Schwere Segmente (Transition-Paare mit vielen Overlays) dediziert mit `-preset ultrafast` oder als 2-Step (Basis-Transition als PCM/crf-15-Intermediate → Overlay-Pass; Overlay-Inputs mit `-t` bis zum Enable-Ende begrenzen).
- Concat per Demuxer mit `-c copy`; Master-Audio separat bauen (siehe `audio.md`) und unter das Concat-Video muxen.
- **Planned- vs. Container-Timeline:** mp4-Containerdauern sind pro Segment ~10–17 ms länger als geplant (AAC-Padding). Alles was auf der finalen Timeline platziert wird (SFX-Events!), stückweise remappen: `actual_start + (t − planned_start)` pro Segment.

## Whisper-Nachbearbeitung (Pflicht im Generator)

1. Tokens mit führendem Bindestrich („Live", „-Online", „-Workshop") zum Vorgänger mergen.
2. **Onset-Audit:** 4-kHz-Mono-Hüllkurve (10-ms-RMS) der Schnitt-Timeline exportieren; jedes Wort mit vorausgehender Pause gegen den echten Energie-Anstieg prüfen. Whisper ist nach Pausen oft 0,2–0,3 s zu früh. Detektor-Bias beachten: −0,15 s zur Anstiegsflanke ist normal, kein Fehler — nur echte Ausreißer korrigieren.
3. Korrekturen als `ONSET_FIX`-Dict im Generator, mit assert (jeder Key trifft exakt ein Wort). Nie Rohdaten-Dateien editieren.

## QC-Gates (vor jeder Lieferung, alle Pflicht)

| Prüfung | Werkzeug | Bestanden wenn |
|---|---|---|
| Freezes | `freezedetect=n=0.001:d=0.4` | 0 Treffer |
| A/V-Länge | `ffprobe stream=duration` | Differenz < 0,1 s |
| Loudness | `ebur128` | −14 LUFS ±0,5 · TP ≤ −1,2 dB |
| Sub-Kontiguität | Parser übers Render-Skript | keine Überlappungen, keine Mikro-Lücken 0–0,2 s, alle Standbild-Enables halboffen |
| Zeilenwechsel | Frame-Strips (Untertitelzone croppen, 5–6 Frames vstack) an 2–3 Wechseln | kein Leerframe, kein Doppel-Highlight |
| Ton-Sync | silencedetect Concat vs. Final | Pausenpositionen ±30 ms |
| SFX-Sync | Events vs. Overlay-Enables | Pop = Onset +0,04 s |

Freezes können zufällig pro Render-Lauf entstehen (stockende Quell-Reads) — ein einmal sauberer Durchlauf beweist nichts für den nächsten. Nach JEDEM Re-Render neu prüfen.

## Frames sind die Wahrheit, Sekunden die Schreibweise

Der `cut-plan.json` führt alle Zeiten in **Sekunden**. Frames entstehen erst im
Generator, aus der tatsächlichen fps des Materials — `frame = round(sekunden * fps)`.

- **Nie Frame-Konstanten in Regeln oder Plänen.** Eine Transition ist „0,18 s",
  nicht „6 Frames": bei einem 60-fps-Kunden dauert sie sonst die Hälfte.
- **Animationsfortschritt gegen `dauer_frames - 1` normalisieren**, nicht gegen
  `dauer_frames`. Sonst erreicht die Kurve nie 1,0, der Snap-Pop landet dauerhaft
  unter seiner Zielgröße und nichts schlägt an. Vollständige Herleitung und
  Rundungstabelle: `animation-kurven.md` Abschnitt 3.
- **Dauern, die Material enthalten müssen** (Segmentlänge, Gesamtlaufzeit),
  werden mit `ceil()` aufgerundet; **Zeitpunkte** mit `round()`. Nie mischen.

## Umgebungs-Eigenheiten

- ffmpeg-Version einmal prüfen (`ffmpeg -version`, `ffmpeg -h filter=xfade`) und Fähigkeiten in der Kunden-Config notieren. 4.4: kein `xfade=zoomin` → `hblur` als Snap-Ersatz.
- Nach jedem nachträglichen scale/crop `setsar=1` setzen (krumme SAR bricht Concat).
- Rotations-Metadaten: `ffprobe` zeigt bei Phone-Clips oft 1920×1080 trotz Hochkant — immer einen echten Frame extrahieren und Maße prüfen, bevor gecroppt wird.
- Cloud-Sync-Ordner (OneDrive/Dropbox „Files on Demand"): Quellen vorher hydratisieren, sonst stille Lese-Stalls → verkürzte Video-Spuren.
- Deploy-Checkliste bei Timing-Änderungen: Render-Skript + events.json + SFX-WAV zusammen erneuern — nie nur das Skript.
- **Getrimmte Standalone-Dateien immer re-encodieren.** `-ss` mit `-c copy` schneidet auf den nächsten Keyframe und hinterlässt eingefrorene Frames am Anfang — die dann im Freeze-Scan als Fehler auftauchen, deren Ursache man an der falschen Stelle sucht. Richtig: `ffmpeg -ss <in> -i quelle.mp4 -to <out> -c:v libx264 -c:a aac ziel.mp4`. Innerhalb der Pipeline gilt das ohnehin, weil jedes Segment neu kodiert wird.
