---
name: ai-video-cutter
description: Verwandelt Rohvideos (Talking-Head, Interviews, Event-Material) in fertige Social-Media-Videos — geschnitten, mit Karaoke-Untertiteln und animierten Emphasis-Captions im eigenen CI, Zoom-Rhythmus, Sound-Effekten und gemastertem Ton. IMMER verwenden, wenn ein Video geschnitten, gekürzt, untertitelt oder für Social Media aufbereitet werden soll — auch bei Formulierungen wie „mach mir ein Reel daraus", „Video für Instagram/LinkedIn", „Untertitel drauf", „schneid das zusammen", „aus dem Webinar einen Clip", oder wenn einfach eine Videodatei mit dem Wunsch nach einem fertigen Ergebnis übergeben wird. Beim ersten Einsatz für einen neuen Kunden zuerst das Setup-Interview führen (references/setup-interview.md).
---

# AI Video-Cutter

Rohvideo rein → fertiges, publizierbares Video raus. Dieser Skill bündelt das Wissen einer kompletten Editing-Masterclass: Schnittrhythmus, Wort-genaue Karaoke-Untertitel, animierte Highlight-Captions, Sound-Design und Ton-Mastering — reproduzierbar mit ffmpeg, ohne Schnittprogramm.

**Grundprinzip: Das Ergebnis muss aussehen wie von einem Profi-Cutter — nicht wie „automatisch generiert".** Jede Regel hier existiert, weil ihre Verletzung sichtbar oder hörbar ist.

## Zwei Wissensebenen (Architektur — strikt einhalten)

- **Dieses Plugin = Allgemeinwissen.** Regeln, QC, Technik — zentral gepflegt, kommt per Plugin-Update. Plugin-Dateien nie lokal editieren oder kopieren-und-anpassen.
- **Kundenordner = Kundenwissen.** `kunden-config.yaml`, `marken-profil.md`, `kunden-learnings.md`, Fonts/Logo, Referenz-Videos — lebt lokal beim Kunden, wird vom Skill angelegt und gepflegt. Details und Ordnerstruktur: `references/learnings-system.md`.

## Update-Check (einmal pro Unterhaltung, still)

1. Installierte Version aus `.claude-plugin/plugin.json` dieses Plugins lesen (Feld `version`) — nie raten, nie hart annehmen.
2. Aktuelle Version per Web-Abruf holen — **immer mit frischem Cache-Buster**, sonst liefert das CDN minutenlang einen alten Stand:
   `https://raw.githubusercontent.com/bauerchristoph-de/mg-video-cutter/main/.claude-plugin/marketplace.json?nc=<zufallszahl>` → Feld `metadata.version`. Die Zufallszahl bei jedem Abruf neu würfeln, nie einen festen Wert verwenden.
3. Beide Versionen **numerisch nach Major/Minor/Patch vergleichen**, nie als Text — 0.10.0 ist höher als 0.9.0.
4. Ist die Online-Version höher, dem Nutzer EINEN kurzen Hinweis geben: „Für dein AI-Paket gibt es Version X.Y.Z — bitte einmal in den Einstellungen → Plugins beim Marketplace auf ‚Synchronisieren' klicken und danach eine neue Unterhaltung starten." Danach normal weiterarbeiten — den Arbeitsfluss nie blockieren, den Hinweis nie wiederholen.
5. Ist die Online-Version gleich oder **niedriger**: still weiterarbeiten, nichts melden. Eine niedrigere Online-Version bedeutet praktisch immer einen zwischengespeicherten Abruf. **Niemals daraus schließen, im Repo sei etwas kaputt, und niemals Versionsfelder ändern oder eine Korrektur vorschlagen.** Real passiert am 28.08.2026: Eine Installation meldete online 0.4.2 bzw. 0.1.2, im Repo standen tatsächlich 0.6.0 bzw. 0.2.0 — die empfohlene „Reparatur" hätte funktionierende Releases beschädigt.
6. Abruf nicht möglich (kein Internetzugriff) → still überspringen, nie erwähnen.

## Pflicht-Lesereihenfolge

1. `kunden-config.yaml` im Kundenordner — CI, Fonts, Kanäle, Intensität. **Fehlt sie, zuerst das Setup-Interview führen** (`references/setup-interview.md`) und die Config anlegen. Nie mit geratenen Farben/Fonts arbeiten.
2. `marken-profil.md` im Kundenordner — die angelernte Brand Voice (Tonalität, Wortschatz, Hooks, Video-Stil je Account). Fehlt es, die Marken-Analyse nachholen (`references/marken-analyse.md`) — ohne Profil keine Captions.
3. `kunden-learnings.md` im Kundenordner — alles, was dieser Kunde dem System schon beigebracht hat. Anwenden statt wiederholen.
4. `references/schnitt-regeln.md` — Schnitt, Zooms, Transitions, Pausen.
5. `references/captions.md` — Untertitel-System (Karaoke + Emphasis-Presets, vermessener Referenz-Standard, Kontrast-Gate).
6. `references/hooks.md` — Hook-Overlays (Creator-Stil, Positionsregeln).
7. `references/audio.md` — Ton-Pipeline (Fades, Master, SFX, bekannte Fallen).
8. `references/render-technik.md` — Render-Architektur und Pflicht-QC (erst vor dem Bauen nötig).
9. `references/qc-parameter.md` — die vollständige Parameterliste der Qualitätskontrolle (erst vor der Lieferung nötig, dann aber komplett).

**Standards-Echo (Pflicht):** Vor dem ersten Render eines Videos in 5–8 Stichpunkten auflisten,
welche Standards aus den References angewendet werden (Untertitel-Werte, Position, Kontrast-Maßnahme,
Hook-Position, SFX-Plan). Wer das Echo nicht schreiben kann, hat die References nicht gelesen —
beide vom Kunden reklamierten Fehlerserien eines echten Builds hatten genau diese Ursache.

## Workflow (verbindlich, mit Freigabe-Schleifen)

Der Kunde gibt pro Schritt frei und korrigiert sekundengenau — der Workflow ist darauf ausgelegt. Nie mehrere Schritte ohne Rückmeldung durchziehen.

### 0 · Setup (einmalig pro Kunde)
Setup-Interview → `kunden-config.yaml` (CI-Farben, Fonts, Logo, Kanäle, Ton-Intensität, Ziel-Plattformen) **plus Marken-Analyse** → `marken-profil.md`: Der Kunde pastet Website und Social-Accounts (mehrere pro Kanal erlaubt) und legt 3–7 typische Videos ab; das System analysiert Texte UND Videos (Transkript, Sprechstil, Schnitttempo, visueller Stil) und lernt daraus belegte Brand-Voice-Muster (`references/marken-analyse.md`). Danach gelten Config + Profil für jedes Video automatisch.

### 1 · Briefing (pro Video, 2 Minuten)
Klären, bevor irgendwas gerendert wird: Ziel des Videos (organisch / Ad / beides), Ziellänge, Plattform + Format (9:16 / 16:9 / 1:1), was ist die Kernbotschaft, gibt es einen CTA. Eine kurze Rückfrage-Runde — nicht zehn.

### 2 · Transkript + Analyse
Audio extrahieren, mit Whisper transkribieren (`word_timestamps=True`, Modell medium, `vad_filter=False`). Wort-Timings sind das Rückgrat von allem — aber Whisper hat bekannte Fehler, die korrigiert werden müssen (Bindestrich-Tokens, verschobene Onsets nach Pausen; Details in `references/audio.md` und `references/render-technik.md`).

**Bild-Analyse gehört dazu:** Luma/Sättigung des Materials messen (`signalstats`). Ist das Material flau oder high-key (kein Schwarzpunkt, Sättigung < 0,10), dem Kunden ein dezentes Color Grading VORSCHLAGEN und bei Ja umsetzen — nie ungefragt, und nie auf Fremd-Quellclips (Reaction-Splits) anwenden.

### 3 · Schnittplan (Freigabe-Dokument)
Als Tabelle: Segment | Quellzeit in/out | Zoomstufe | Untertitel-Modus (karaoke/emphasis) | SFX. Dazu in 3 Sätzen: dramaturgische Idee (Hook → Kernaussagen → CTA), welche Stellen Emphasis bekommen und warum. **Erst nach Freigabe bauen.**

### 4 · Build — mit den mitgelieferten Skripten, nie nachgebaut
Die Skripte in `scripts/` sind die ausführbare Hälfte dieses Skills. Sie werden benutzt, nicht neu geschrieben — jede Eigenbau-Pipeline hat bisher dieselben Fehler reproduziert (Chip an der Ascender- statt Ink-Box, verschluckte Wörter, unlesbare Zeilen).

```bash
python3 scripts/contrast_probe.py --video cut.mp4 --plan cut-plan.json --apply
python3 scripts/build.py --config kunden-config.yaml --plan cut-plan.json --out build/
python3 scripts/make_sfx.py --events build/events.json --duration <sek> --out build/sfx.wav --check
# ffmpeg-Overlay + Master (video-spezifisch, Rezepte in references/render-technik.md)
python3 scripts/qc.py --video final.mp4 --build build/ --plan cut-plan.json
```

Pro Video wird ausschließlich `cut-plan.json` geschrieben (Aufbau: `scripts/README.md`, Vorlage: `scripts/cut-plan.example.json`). Fehlt eine Fähigkeit im Skript, gehört sie ins nächste Release — nicht in den Projektordner. Architektur und Render-Rezepte: `references/render-technik.md`.

### 5 · QC vor Lieferung — alle Parameter, hartes Gate

**Die Qualitätskontrolle prüft am Ende jeden Parameter**, nicht nur das, was auffällig
aussieht: Technik, Untertitel, Bild, Inhalt, Marke, Recht. Vollständige Tabelle mit
Sollwerten, Messverfahren und Konsequenz: `references/qc-parameter.md`.

```bash
python3 scripts/qc.py --video final.mp4 --build build/ --plan cut-plan.json \
        --config kunden-config.yaml --format reel
```

**Die Kunden-Config gehört immer mit dazu.** Ohne `--config` laufen die technischen Gates
plus die beiden Zahlen-Gates (die brauchen keine Config); es fehlen dann Glossar,
Pflichtphrasen, CTA-Kanaltreue, Sprechtempo und Formatvorgaben — also genau die Prüfungen,
die kundenspezifisch wehtun.

Technik: A/V-Dauer < 0,1 s · Freeze-Scan = 0 · −14 LUFS ±0,5 · True Peak ≤ −1,2 dB ·
Fremdquellen ≤ 2 dB Differenz · Auflösung und Laufzeit laut Format.

Untertitel und Bild: Karten-Kontinuität · Vollständigkeit (jedes Wort sichtbar) ·
Onset-Stichproben gegen die RMS-Hüllkurve · **Lesbarkeits-Gate** (Luminanz der Textzone —
helle Schrift auf hellem Grund ohne Scrim ist durchgefallen, egal was die Timing-Gates
sagen) · **Kollisions-Check** (kein Text über Gesicht, Händen, Logos, Bildschrift) ·
SFX-Peaks gegen Animations-Onsets.

Inhalt — hier entstehen die teuren Fehler:
- **Zahlen-Rechenprüfung.** Jede Prozentrechnung im Endtext muss aufgehen. Whisper
  vertippt sich bei Beträgen **hochkonfident** (gemessen: falsche Zahlen mit p = 0,94 bis
  0,98) — die Konfidenz taugt deshalb nicht als Detektor, die Arithmetik schon.
- **Zahlen-Deckung.** Jede angezeigte Zahl muss auch gesprochen worden sein.
- **Glossar.** Kein bekannter Transkriptionsfehler des Kunden darf im Endtext stehen.
- **Pflichtphrasen.** Rechtliche Weichmacher („in der Regel", „meine Erfahrung",
  Verweis auf den Fachberater) müssen den Schnitt überleben — fallen sie weg, ändert sich
  das Aussage-Niveau, nicht nur der Stil.
- **CTA-Kanaltreue.** Longform trägt den CTA-Block, Reels enden nach dem Abbinder.
- Sprechtempo im Profil ± Toleranz (Ausreißer deuten auf Fehlschnitt).

`scripts/qc.py` beendet sich mit Fehlercode, wenn ein Gate reißt. **Den erzeugten
Kontaktbogen `qc-frames.jpg` trotzdem immer ansehen** — Zahlen erkennen nicht, dass helle
Schrift auf einem weißen Hemd liegt.

**Die Gates gelten unabhängig vom Freigabemodus.** Wird die manuelle Freigabe nach zehn
sauberen Durchläufen abgeschaltet, bleiben sie an — sie sind der Ersatz für das Augenpaar,
nicht dessen Beifahrer.

### 6 · Lieferung
Master in voller Qualität in den Ordner `fertig/` + kleine Preview (480p) in den Chat. Bei Feedback: Version hochzählen, nie überschreiben.

### 7 · Begleit-Content (optional, nach Video-Abnahme)
Was in der Config unter `begleit_content` aktiviert ist, wird mitgeliefert: Caption pro Kanal, Titel-/Hook-Varianten, Post-Kurzfassung — alles aus dem Transkript, im Kunden-Wording. Regeln: `references/begleit-content.md`.

### 8 · Learnings-Abschluss (Pflicht, nach jeder finalen Abnahme)
Alle Korrekturen der Feedbackrunden kategorisieren: kundenspezifisch → `kunden-learnings.md` bzw. direkt die Config ändern; allgemeingültige Beobachtungen nur im Abschluss-Satz benennen (die zentrale Pflege sammelt sie im direkten Kontakt ein — nichts davon in Kundendateien). Dem Kunden in einem Satz sagen, was das System für ihn gelernt hat. Ablauf und Format: `references/learnings-system.md`. **Dieser Schritt ist der Grund, warum das Produkt mit jedem Video besser wird — nie überspringen.**

## Was dieses System auszeichnet (die Essenz)

- **Ruhe schlägt Dauerfeuer.** Karaoke-Untertitel tragen 80–90 % des Videos ruhig; Emphasis-Momente (max. 3/Minute) wirken nur durch den Kontrast.
- **Alles framegenau und mehrschichtig.** Ein Highlight-Moment = Text-Pop + Punch-Zoom im Video + SFX im selben Frame. Einzeln wirkt nichts davon.
- **Schnitte in die Sprechpause, nie auf den Wortanfang.** Sonst werden Silben verschluckt („Zweitens" → „weitens").
- **Messen statt hören/raten.** Onsets, Pausen, Beats, Loudness — alles wird per RMS/ebur128 gemessen. Timing nach Gehör ist zweimal schiefgegangen, seitdem Pflicht.
- **Ein CI, eine Akzentfarbe.** Konsistenz schlägt Abwechslung; die Akzentfarbe kommt aus der Kunden-Config und ist überall dieselbe (Chip, Keyword, Glow, CTA).
- **Jede Ersetzung im Generator mit Assert, jede Änderung mit maschineller Gegenprüfung.** Stille Fehlschläge haben schon ganze Feedbackrunden gekostet.

## Grenzen

- Kein Ersatz für fehlendes Material: Aus schlechtem Rohvideo (unverständlicher Ton, Dauerwackeln) wird kein gutes Reel — dann ehrlich sagen, was fehlt.
- Musik-Einbindung nur mit lizenziertem Material des Kunden (Envato o. ä.); keine Trending-Sounds, wenn Dritte das Video teilen sollen.
- Rechenzeit: ~2–5 Minuten Renderzeit pro Videominute je nach Rechner — bei Iterationen einplanen.
