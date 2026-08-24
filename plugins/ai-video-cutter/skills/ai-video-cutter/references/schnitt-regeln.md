# Schnitt-Regeln

## Rhythmus & Struktur

- **Talking-Head/Webinar-Clip (60–120 s):** Hook in den ersten 3 s (stärkste Aussage, nie Intro-Floskeln) → Kernaussagen mit Emphasis-Momenten → CTA. Füllwörter, Versprecher, „ähm", doppelte Ansätze rausschneiden — aber Atmung und natürliche Pausen LASSEN, sonst wirkt es gehetzt.
- **Zoomstufen-Wechsel alle 3–5 s** an Satzgrenzen (100 ↔ 112 ↔ 125 %). Der Wechsel ersetzt den B-Roll-Cut, den Talking-Head-Material nicht hergibt.
- **Action-/Event-Material (9:16, 75–90 s):** Hook 0–5 s aus 4–6 schnellen Action-Beats (kein Slow-Mo am Anfang) → Titel auf Musik-Drop → O-Töne mit Bauchbinden → emotionaler Höhepunkt auf Drop → Abbinder. Referenz-Tempo: Median-Shot ~1,5 s.
- Pausen zwischen Aussagen: knapp, aber verständlich — Sprechpausen auf ~0,3–0,5 s kürzen, nie auf 0.

## Schnittpunkte (die wichtigste Regel des ganzen Systems)

**Schnitte gehören in die Sprechpause, nie auf den Wortanfang.**
- Segment-Einstieg ~0,12–0,25 s VOR dem ersten Wort, Ausstieg ~0,15 s NACH dem letzten.
- Plosive/Frikative (D, Z, K, B …) beginnen real bis 0,2 s vor dem Whisper-Onset → Pre-Roll an getrimmten Schnitten ≥ 0,25 s.
- Ton-Crossfades müssen KOMPLETT im Raumton liegen — liegt die Blendzone auf dem Wortanfang, wird die erste Silbe eingeblendet („Zweitens" → „weitens").
- Trick bei knappen Pausen: beide Seiten überlappend aus derselben Quelle schneiden — Raumton mit sich selbst gecrossfadet ist nahtlos.
- Benachbarte Segmente derselben Quelle: aus-Punkt == ein-Punkt (exakt kontiguierlich), sonst spielen Wortanfänge doppelt („Je– Jeden"). Nach jeder Timing-Änderung maschinell prüfen.

## Jump-Cuts kaschieren

- **Punch-in** (zweiter Take +10–15 % Zoom, harter Schnitt) oder B-Roll-Cutaway.
- **Blenden kaschieren Jump-Cuts NICHT** — zwei Takes derselben fast-statischen Einstellung mit Crossfade lesen sich als Einfrieren („es hakt"). Blenden nur zwischen unterschiedlichen Motiven.
- Kein Kurz-Stub: 0,2–0,4 s zurück in einen schon gezeigten Shot wirkt wie ein Ruckler.

## Material-Auswahl (Event-/B-Roll-Material)

- Menschen in Aktion, Gesicht/Emotion sichtbar. Keine Nur-Beine-Ausschnitte, statischen Motive, wackligen Schwenks, nichts was „beschleunigt" aussieht.
- Pointen vollständig lassen (nicht vor dem Grinsen/High-Five schneiden); Versprecher und „ja"-Anläufe am Interviewanfang weg.
- Jede Clip-Auswahl visuell prüfen (Kontaktbogen/Framesheet) — nie nach Dateiname oder Transkript raten.
- Keine Standbilder als Lückenfüller. Wenn ein Foto inhaltlich unschlagbar ist: sanfter Push-in (8–12 % Zoom, Ease-OUT) oder Polaroid-Karten-Look (B-Roll läuft unscharf weiter, Fotos poppen als gedrehte Karten mit Schatten rein).
- Slow-Mo als **Speed-Ramp auf den Action-Peak** (Anlauf normal, ab exakt dem Peak 0,5×; nur 60-fps-Material). Nie zwei Dauer-Slow-Mos hintereinander.

## Ad-Ausspielung vs. organisch (dasselbe Rohmaterial, zwei Schnitte)

Im Briefing wird das Ziel festgelegt — die Ausspielungen unterscheiden sich systematisch:
- **Organisch:** Ziellänge darf atmen (45–120 s), Hook stark aber inhaltsgetrieben, CTA weich (folgen, kommentieren, Link in Bio), Emphasis-Dichte standard.
- **Ad:** kürzer (15–45 s), Hook noch härter (erste Aussage = stärkstes Versprechen oder stärkste Zahl), CTA explizit und früh angelegt (`cta-arrow` am Ende Pflicht), auf Stummschaltung optimieren (Captions tragen die Botschaft allein), Safe-Zones strenger (Ad-Overlays der Plattform), keinerlei fremde Musik/Sounds (Lizenz + Brand Safety).
- Beide Fassungen aus demselben Schnittplan ableiten: die Ad-Fassung ist die verdichtete Kernaussage-Sequenz des organischen Cuts, nicht ein neuer Schnitt von Null.

## Musik (falls Musikbett gewünscht)

- BPM + Beatgrid messen (librosa), Hits/Stille/Drops per RMS im 0,1-s-Raster — **nie nach Gehör timen**. Cuts auf Beat, Titel auf Drop.
- Musik 18–25 dB unter Sprache mit 0,4-s-Rampen; unter Jubel/Action höher. Clips mit eigener Musik muten.
- Nur lizenziertes Material (Envato/Artlist). Keine Trending-Sounds, wenn Dritte teilen sollen.
