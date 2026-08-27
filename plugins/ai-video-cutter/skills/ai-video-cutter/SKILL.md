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

## Pflicht-Lesereihenfolge

1. `kunden-config.yaml` im Kundenordner — CI, Fonts, Kanäle, Intensität. **Fehlt sie, zuerst das Setup-Interview führen** (`references/setup-interview.md`) und die Config anlegen. Nie mit geratenen Farben/Fonts arbeiten.
2. `marken-profil.md` im Kundenordner — die angelernte Brand Voice (Tonalität, Wortschatz, Hooks, Video-Stil je Account). Fehlt es, die Marken-Analyse nachholen (`references/marken-analyse.md`) — ohne Profil keine Captions.
3. `kunden-learnings.md` im Kundenordner — alles, was dieser Kunde dem System schon beigebracht hat. Anwenden statt wiederholen.
4. `references/schnitt-regeln.md` — Schnitt, Zooms, Transitions, Pausen.
5. `references/captions.md` — Untertitel-System (Karaoke + Emphasis-Presets, vermessener Referenz-Standard, Kontrast-Gate).
6. `references/hooks.md` — Hook-Overlays (Creator-Stil, Positionsregeln).
7. `references/audio.md` — Ton-Pipeline (Fades, Master, SFX, bekannte Fallen).
8. `references/render-technik.md` — Render-Architektur und Pflicht-QC (erst vor dem Bauen nötig).

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

### 4 · Build
Generator-Skript erzeugt alle Assets (Untertitel-PNGs, Emphasis-Sequenzen, SFX-Spur) und ein resumables Render-Skript. Architektur und Pflicht-Prüfungen in `references/render-technik.md` — die dort beschriebenen QC-Gates sind nicht optional, jede einzelne Prüfung hat schon reale Fehler gefangen.

### 5 · QC vor Lieferung (hartes Gate)
- Freeze-Scan (`freezedetect`) = 0 Treffer
- Video- vs. Audio-Streamdauer < 0,1 s Differenz
- Loudness −14 LUFS ±0,5, True Peak ≤ −1,2 dB; bei Fremd-Quellclips: Sprach-Lautheit über alle Quellen angeglichen (≤ 2 dB Differenz)
- Frame-Strips an 2–3 Untertitel-Zeilenwechseln (kein Leerframe, kein Doppel-Highlight)
- **Lesbarkeits-Gate:** Frames an den Kartenmitten von mindestens jeder 3. Untertitel-Karte ziehen und ANSEHEN + Luminanz der Textzone messen — helle Schrift auf hellem Grund (weißes Hemd!) ohne Scrim = durchgefallen, egal was die Timing-Gates sagen (Kontrast-Gate in `references/captions.md`)
- **Kollisions-Check:** Untertitel/Hook liegen nicht über Gesicht, Händen, Logos oder Schrift im Bild
- **Vollständigkeits-Gate:** jedes Transkript-Wort erscheint in Karaoke oder Emphasis — kein Wort fehlt
- Onset-Stichprobe: 3–5 Wörter nach Sprechpausen gegen die RMS-Hüllkurve
- SFX-Events gegen Animations-Onsets abgeglichen (maschinell, nicht nach Gehör); SFX-Peaks gemessen, nicht Dateienden

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
