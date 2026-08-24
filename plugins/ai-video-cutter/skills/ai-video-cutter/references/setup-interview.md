# Setup-Interview — einmalig pro Kunde

Ziel: In 10–15 Minuten alles erfassen, damit jedes künftige Video ohne Rückfragen im richtigen Look entsteht. Ergebnis ist die `kunden-config.yaml` (Template in `assets/kunden-config.yaml`) im Kundenordner.

## Schritt 0 — Geteilten Bestand prüfen (Interop mit anderen Paketen)

Existieren `kunden-config.yaml` und `marken-profil.md` bereits im Arbeitsordner (z. B. vom AI Post-Generator angelegt)? Dann übernehmen statt neu erheben — nur die video-spezifischen Teile ergänzen (Intensität, Untertitel-Position, brand-referenz-Videos, Technik-Check).

## Ablauf

Stelle die Fragen gesprächig und in Blöcken, nicht als Formular. Wo Material existiert (Website, Instagram-Profil, Brand-Guide-PDF), zuerst selbst nachschauen und nur bestätigen lassen — der Kunde soll merken, dass das System mitdenkt.

### Block 1 — Marke & CI
- Website + Social-Profile ansehen: Welche Farben trägt die Marke wirklich? (Nicht fragen „welche Farben habt ihr" — Vorschlag machen: „Ich sehe Rot #EE1717 als CTA-Farbe, das nehmen wir als Akzent — passt das?")
- **Genau EINE Akzentfarbe** festlegen (CTA-/Signalfarbe). Mehr gibt es nicht — Konsistenz ist der Look.
- Font: Welcher Font läuft auf Website/Werbemitteln? Falls kein Lizenz-Font verfügbar: Inter als hochwertiger Default (Bold für Karaoke, Black für Emphasis, SemiBold für Unterzeilen). Font-Dateien (ttf/otf) einsammeln und im Projektordner ablegen.
- Logo als PNG mit Transparenz (für Abbinder/Wasserzeichen, falls gewünscht).

### Block 2 — Inhalte & Kanäle
- Welche Plattformen? (bestimmt Formate: 9:16 Reels/Shorts/TikTok, 16:9 YouTube/Website, 1:1 Feed)
- Welche Video-Typen kommen regelmäßig? (Talking-Head, Webinar-Ausschnitte, Event-Material, Interviews)
- Wer spricht? (ein Sprecher / mehrere → ggf. zweite Highlight-Farbe für Sprecher B — einzige erlaubte Ausnahme von der Ein-Akzent-Regel)
- Gibt es wiederkehrende CTAs? (Workshop-Anmeldung, Link in Bio, Termin buchen) → als Standard-CTA-Bausteine notieren.

### Block 2b — Marken-Analyse (das Herzstück des Setups)
- Kunde pastet alle Quellen rein: Website, Instagram, Facebook, LinkedIn, TikTok, YouTube — mehrere Accounts pro Kanal erlaubt (Firma + Personal Brand). Zusätzlich legt er 3–7 typische Videos in `brand-referenz/`.
- Vollständige Analyse nach `references/marken-analyse.md` fahren: Texte pro Account UND Videos (Transkript/Sprechstil, Frames/visueller Stil, gemessenes Schnitttempo) → belegte Muster → `marken-profil.md` schreiben → Kurzfassung dem Kunden zur Bestätigung zeigen.
- Kurzfassung des Ergebnisses je Kanal zusätzlich in `wording_notizen` der Config (schnelles Nachschlagen; bei Widerspruch gilt das Markenprofil).

### Block 2c — Begleit-Content
- Soll zu jedem Video automatisch eine Caption mitgeliefert werden? Für welche Kanäle? (→ `begleit_content` in der Config)

### Block 3 — Tonalität
- Intensität wählen und mit Beispielen zeigen: **ruhig** (B2B/konservativ: kein Chip, aktuelles Wort in Akzentfarbe, keine SFX) / **standard** (Chip-Highlight, dosierte Emphasis, dezente SFX) / **hart** (Creator-Style: stärkere Pops, mehr Jitter, hörbare SFX). Im Zweifel standard — nachschärfen ist leichter als zurückrudern.
- Groß-/Kleinschreibung der Emphasis-Captions (Versalien = Default).
- Duzen/Siezen in Captions, falls Text gekürzt werden muss.

### Block 4 — Technik & Material
- Wo landet Rohmaterial? (fester Ordner vereinbaren — „Rohvideo rein, fertiges Video raus" braucht einen definierten Ort)
- Musik: Hat der Kunde Envato/Artlist-Zugang? Sonst: Videos ohne Musikbett (Talking-Head trägt sich selbst) oder Kunde lizenziert pro Projekt.
- ffmpeg-Umgebung einmal prüfen: `ffmpeg -version` (Feature-Unterschiede zwischen Versionen beachten — z. B. existiert `xfade=zoomin` erst ab 5.x; verfügbare Transitions mit `ffmpeg -h filter=xfade` prüfen und in der Config notieren).

## Abschluss

1. `kunden-config.yaml` ausfüllen und dem Kunden als Zusammenfassung zeigen („So sieht dein Setup aus").
2. **Probelauf anbieten:** ein kurzes Testvideo (30–60 s) aus vorhandenem Material schneiden — kalibriert Erwartungen und Intensität besser als jede Beschreibung.
3. Ordnerstruktur anlegen (siehe `learnings-system.md`): `rohmaterial/`, `brand-referenz/`, `fertig/`, `projekte/`, `assets/` + leere `kunden-learnings.md` mit Kopfzeile; `marken-profil.md` entsteht in der Marken-Analyse.
