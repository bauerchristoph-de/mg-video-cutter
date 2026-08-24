# Marken-Analyse — die Marke einmal komplett anlernen (Teil des Setups)

Einmalig beim Setup (und danach bei Bedarf auffrischbar): Die komplette Außendarstellung des Kunden wird analysiert — Texte UND Videos — und zu einem `marken-profil.md` im Kundenordner verdichtet. Dieses Profil ist ab dann die Grundlage für jede Caption, jede Untertitel-Formulierung, jede Stil-Entscheidung. Ziel: Das System kennt die Marke so gut, dass der Kunde seine eigenen Ergebnisse nicht mehr von selbstgemachten unterscheiden kann.

## Eingaben (vom Kunden, einfach reingepastet)

- Website-URL(s)
- Social-Accounts: Instagram, Facebook, LinkedIn, TikTok, YouTube — **mehrere Accounts pro Kanal sind ausdrücklich erlaubt** (z. B. Firmenaccount + Personal Brand des Gründers). Jeder Account wird separat analysiert und im Profil eigenständig beschrieben.
- Optional: Brand-Guide-PDF, bestehende Werbetexte, E-Mail-Beispiele.
- Für die Video-Analyse: 3–7 typische Videos des Kunden (die er selbst als „so klingen/aussehen wir" empfindet). Wenn Reels nicht direkt abrufbar sind: Kunde legt die Videodateien in `brand-referenz/` im Kundenordner — das dauert ihn 5 Minuten und ist der wertvollste Input des ganzen Setups.

## Ablauf

### 1 · Material einsammeln
Website-Seiten lesen (Start, Über-uns, Angebot); pro Social-Account die letzten 10–15 Post-Texte erfassen. Was nicht automatisch abrufbar ist (Login-Walls), vom Kunden als Screenshots/Copy-Paste nachliefern lassen — lieber nachfragen als mit dünner Datenbasis raten.

### 2 · Video-Analyse (Pflicht, nicht nur Text!)
Für jedes Referenz-Video in `brand-referenz/`:
- **Audio transkribieren** (Whisper) → Sprechstil: Tempo, Satzlänge, Füllwort-Muster, Anrede, typische Einstiege und Abschlüsse, wiederkehrende Phrasen.
- **Frames extrahieren** (1/s) und sichten → visueller Stil: Setting, Farbwelt in der Praxis, Text-Overlays/Untertitel-Stil (falls vorhanden: Position, Farben, Animationsgrad), Logo-Nutzung.
- **Schnitt-Charakteristik messen**: Szenenwechsel zählen (ffmpeg `select='gt(scene,0.3)'`) → tatsächliches Schnitttempo; Musik ja/nein und Charakter.
Ergebnis pro Video 3–5 Beobachtungssätze; über alle Videos dann die Muster.

### 3 · Muster ableiten (das Herzstück)
Aus allem zusammen klare, BELEGTE Muster extrahieren — jede Aussage mit 1–2 Originalzitaten/Beispielen als Beleg. Keine Adjektiv-Wolken („authentisch, nahbar, professionell" beschreibt jeden), sondern operative Merkmale, nach denen man schreiben und schneiden kann:
- **Tonalität**: Anrede (du/sie), Energie-Level, Humor ja/wie, Direktheit, Emotionalität vs. Sachlichkeit — je Kanal/Account getrennt, Unterschiede explizit benennen.
- **Wortschatz**: typische Begriffe und Phrasen (Liste), Fachwort-Niveau, Anglizismen ja/nein, **No-Go-Wörter** (was die Marke nie sagen würde).
- **Satzbau & Rhythmus**: kurz/lang, Fragen als Stilmittel, Zeilenumbrüche, Großschreibung.
- **Themen & Botschaften**: worüber spricht die Marke, was ist das Kernversprechen, wiederkehrende Argumente.
- **Hook- & CTA-Muster**: wie steigen ihre erfolgreichen Posts ein, wie fordern sie auf.
- **Emoji-/Hashtag-Verhalten**: welche, wie viele, wo.
- **Video-Stil**: Sprechweise, Schnitttempo, bisheriger Untertitel-Stil, Musik-Charakter, Settings.

### 4 · Profil schreiben und validieren
`marken-profil.md` nach dem Format unten schreiben. Dann dem Kunden die 5 wichtigsten Erkenntnisse als Kurzfassung zeigen: „So liest sich eure Marke — stimmt das Bild?" Seine Korrekturen einarbeiten. Erst dann ist das Setup abgeschlossen.

## Format marken-profil.md

```markdown
# Markenprofil <Kunde> — Stand <Datum>
Analysierte Quellen: <URLs, Accounts mit Post-Anzahl, N Videos>

## Marke in 3 Sätzen
<Kernversprechen, Zielgruppe, Positionierung — aus der Analyse, nicht aus der Selbstbeschreibung>

## Account: <Name> (<Kanal>)
### Tonalität   <operative Beschreibung + 2 Belegzitate>
### Wortschatz  <typische Begriffe/Phrasen als Liste; No-Go-Wörter>
### Satzbau     <Muster + Beleg>
### Hooks & CTAs <Muster + je 2 Beispiele>
### Emojis & Hashtags <konkret>
## Account: … (je Account ein Block)

## Video-Stil
<Sprechweise, Tempo (Schnitte/Minute gemessen), Untertitel-Stil bisher, Musik, Settings>

## Konsequenzen für unsere Videos
<5–8 konkrete Regeln: was übernehmen wir, was machen wir bewusst besser (mit Begründung)>
```

## Pflege

- Das Profil ist ein lebendes Dokument: Wording-Feedback aus Feedbackrunden wird hier nachgeschärft (nicht nur in kunden-learnings.md — das Profil ist die Quelle, die Learnings sind das Protokoll).
- Bei Rebranding, neuem Account oder spürbarer Stil-Änderung: Analyse auf Zuruf neu laufen lassen (alte Fassung datiert archivieren).
- `wording_notizen` in der kunden-config.yaml bleibt die Kurzfassung fürs schnelle Nachschlagen; bei Widerspruch gilt das Markenprofil.
