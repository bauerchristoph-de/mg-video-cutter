# Lösungsbibliothek — der Einstieg über den Fall, nicht über die Datei

Dieser Skill ist gewachsen. Damit Umfang nicht Suchen bedeutet, ist das hier der
Index: **Fall links, Lösung rechts, mit dem Wert, auf den es ankommt.**

Nicht alles lesen. Die Pflicht-Lesereihenfolge in der SKILL.md ist der Grundstock;
alles Weitere wird über diese Tabellen gezielt nachgeschlagen.

---

## A · Nach Auftrag

| Der Kunde sagt … | Zuerst lesen | Dann |
|---|---|---|
| „Mach ein Reel aus dem Webinar" | `schnitt-regeln.md` → Talking-Head | Standardablauf |
| „Video für Instagram, hochkant" | `captions.md` → Position 9:16 | Hormozi-Zone 62–70 %, UI-Zonen meiden |
| „Das gleiche nochmal als Ad" | `schnitt-regeln.md` → Ad vs. organisch | 15–45 s, harter Hook, `cta-arrow` Pflicht |
| „Untertitel drauf, sonst nichts" | `captions.md` → Preset `karaoke` | Onset-Audit trotzdem Pflicht |
| „Ruhiger, wir sind B2B" | `captions.md` → Preset `quiet` | plus Overshoot 1.30–1.40 (`animation-kurven.md`) |
| „Mach 10 Varianten mit anderen Preisen" | `schnitt-regeln.md` → Ad vs. organisch | ein Schnittplan, n `cut-plan.json` — Stil bleibt identisch |
| „Ich will vorher sehen, bevor ihr rendert" | Workflow Schritt 3 in der SKILL.md | Schnittplan als Freigabe-Dokument, dazu Standbilder der Kernframes |
| „Der Titel soll knallen" | `hooks.md` | Creator-Stil, ein Keyword auf Chip, nie über dem Gesicht |
| „Erstes Video für diesen Kunden" | `setup-interview.md` + `marken-analyse.md` | ohne Config und Markenprofil wird nicht gebaut |
| „Und ein Post-Text dazu" | `begleit-content.md` | nur was in der Config aktiviert ist |
| „Event-Zusammenschnitt" | `schnitt-regeln.md` → Action-Material | Median-Shot ~1,5 s, jeder Clip nur einmal |

---

## B · Nach Symptom — was ist kaputt

| Symptom | Ursache und Lösung | Steht in |
|---|---|---|
| Silbe am Schnitt verschluckt („Zweitens" → „weitens") | Schnitt liegt auf Sprache. `pausen_scan.py` laufen lassen, Schnitt in die Pausenmitte | `schnitt-regeln.md`, `scripts/pausen_scan.py` |
| Untertitel wirken ab der Mitte asynchron | AAC-Priming-Drift beim Segment-Concat | `audio.md` → Master-Kette Schritt 1 |
| Untertitel unlesbar (weiß auf hellem Hemd) | Kontrast-Gate übersprungen. `contrast_probe.py`, dann Scrim oder Position | `captions.md` → Kontrast-Gate |
| Chip sitzt zu hoch, Schrift wirkt nicht mittig | Ausrichtung an der Ascender- statt Ink-Box | `captions.md` → Referenz-Standard |
| Chips springen beim Wortwechsel | Ink-Box je Wort statt einmalig am Referenzstring gemessen | `captions.md` |
| Chip-Breiten stimmen systematisch nicht | Laufweite beim Messen weggelassen, oder gegen einen Ersatz-Font gemessen | `captions.md` → Referenz-Standard |
| Ganze Halbsätze fehlen in den Untertiteln | Emphasis-Unterdrückung auf Karten- statt Wort-Ebene | `captions.md` → Vollständigkeits-Regel |
| Leerframe / Doppel-Highlight am Zeilenwechsel | Overlay-Fenster inklusiv statt halboffen | `captions.md` → Timing-Regeln |
| Pop ist hörbar vor dem Bild | SFX auf den Animationsstart statt auf den Peak gelegt | `animation-kurven.md` → Abschnitt 4 |
| Snap-Pop wirkt weich / erreicht die Zielgröße nicht | Fortschritt gegen `n` statt `n-1` normalisiert | `animation-kurven.md` → Abschnitt 3 |
| Push-in bremst gefühlt aus | Skalierung linear statt wahrnehmungsgerecht interpoliert | `animation-kurven.md` → Abschnitt 2 |
| Eigener Sprecher ist die leiseste Stimme im Video | Fremdquellen nicht pro Quelle gemessen und angeglichen | `audio.md` → Fremdmaterial |
| Klack an Segmentgrenzen | 8-ms-Kantenfade fehlt | `audio.md` → Segment-Ebene |
| Audio ist am Ende länger als das Video | `loudnorm` nach `amix` (One-Pass streckt) | `audio.md` → bekannte Fallen |
| SFX liegt hörbar neben dem Schnitt | Kunden-SFX-Datei ungeprüft übernommen (Stille am Anfang) | `audio.md` → Kunden-SFX-Dateien |
| Jump-Cut „hakt" trotz Blende | Blenden kaschieren Jump-Cuts nicht — Punch-in nutzen | `schnitt-regeln.md` |
| Kunde erkennt wiederholte Clips | dHash-Wiederholungs-QC nicht gelaufen | `schnitt-regeln.md` → Wiederholungen |
| Zahl im Video ist falsch, Whisper war sich sicher | Konfidenz taugt nicht, Arithmetik schon | `qc-parameter.md` → Zahlenprüfung |
| Freeze im fertigen Video | Freezes entstehen pro Render-Lauf neu — nach JEDEM Re-Render prüfen | `render-technik.md` |
| Hochkant-Clip wird falsch gecroppt | Rotations-Metadaten lügen — echten Frame extrahieren | `render-technik.md` → Umgebung |
| Render bricht mitten ab, Datei zu kurz | kein Atomic Write | `render-technik.md` → Architektur |
| Quelle liest still stockend, Spur zu kurz | Cloud-Sync-Ordner nicht hydratisiert | `render-technik.md` → Umgebung |

---

## C · Nach Bauteil

**Untertitel** → `captions.md` (7 Presets, Referenz-Standard, Kontrast-Gate,
Kollisions-Regeln, Vollständigkeit) · Kurven und Frame-Werte →
`animation-kurven.md`

**Hook** → `hooks.md` (Stil, Position je Format, Copy-Herkunft)

**Schnitt** → `schnitt-regeln.md` (Rhythmus, Schnittpunkte, Jump-Cuts,
Materialauswahl, Ad vs. organisch, Musik) · maschinelle Prüfung →
`scripts/pausen_scan.py`

**Ton** → `audio.md` (Segment-Fades, Master-Kette, SFX-Synthese, Fremdmaterial,
Fallen)

**Bild und Render** → `render-technik.md` (Generator-Architektur,
Whisper-Nachbearbeitung, Render-Rezepte, Umgebungs-Eigenheiten)

**Qualitätskontrolle** → `qc-parameter.md` (alle Gates mit Sollwert, Messverfahren
und Konsequenz)

**Kundenwissen** → `setup-interview.md`, `marken-analyse.md`,
`learnings-system.md`

**Begleittexte** → `begleit-content.md`

---

## D · Werkzeugkasten

| Werkzeug | Wofür | Wann |
|---|---|---|
| `scripts/pausen_scan.py --report` | Sprechpausen finden, Schnittfenster vorschlagen | **vor** dem Schnittplan |
| `scripts/pausen_scan.py --plan` | Gate: liegt ein geplanter Schnitt auf Sprache? | nach dem Schnittplan, vor dem Build |
| `scripts/contrast_probe.py --apply` | Luminanz der Textzone messen, Scrim-Entscheidung in den Plan | vor dem Build |
| `scripts/build.py` | Overlays, Karten, Emphasis-Sequenzen, `events.json` | Build |
| `scripts/make_sfx.py --check` | SFX-Spur bauen, Peak-Lage gegen die Events messen | Build |
| `scripts/qc.py` | alle Gates, Exit-Code 1 = nicht ausliefern | vor Lieferung |
| `ffmpeg -af loudnorm=print_format=json` | Lautheit und Gating-Schwelle messen | Analyse, Master |
| `ffmpeg -vf signalstats` | Luma/Sättigung des Materials | Analyse, Grading-Frage |
| `ffmpeg -vf freezedetect` | Standbilder finden | nach JEDEM Render |
| `ffprobe -show_entries format=duration` | A/V-Dauern vergleichen | QC |

**Die Skripte werden benutzt, nicht nachgebaut.** Fehlt eine Fähigkeit, gehört
sie ins nächste Release — nicht in den Projektordner. Ablauf und
`cut-plan.json`-Aufbau: `scripts/README.md`.

---

## E · Die sechs Werte, die nie zur Diskussion stehen

Egal welcher Fall, welcher Kunde, welches Format:

1. Snap-Pop-Overshoot **8,0 %**, Dauer **0,20 s**, Exit **0,15 s**
2. Anzeige-Vorlauf der Karaoke-Zeile **0,10 s**
3. SFX-Pop auf **Animations-Peak + 0,04 s**
4. Zoomstufen **100 / 112 / 125 %**, harte Wechsel
5. Emphasis **max. 3 pro Minute**
6. Master **−14 LUFS ±0,5**, True Peak **≤ −1,2 dBTP**

Abweichungen sind Kunden-Learnings und gehören in `kunden-learnings.md` oder die
Config — nie in einen Einzelfall-Beschluss während des Builds.
