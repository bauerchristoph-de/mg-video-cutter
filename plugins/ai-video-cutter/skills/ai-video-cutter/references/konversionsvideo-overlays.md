# Konversionsvideos (Danke-Seite, Pitch, Angebotsvideo) — Overlays, Varianten, Auslieferung

Gesammelt aus sechs Feedbackrunden (Oktober/November 2026, Webinar-Danke-Seiten-Video mit Angebots-Pitch). Gilt für jedes lange Talking-Head-Video, das am Ende ein Angebot verkauft. Ergänzt `talking-head-schnittfehler.md` (Schnitt, Ton) um das, was nur bei Verkaufsvideos zählt. Beispielcode: `scripts/overlays_beispiel.py`.

## 1 · Aufbau eines Danke-/Pitch-Videos

Dramaturgie: Hook → Warum dranbleiben → Pitch (Inhalt) → Teaser „gleich kommt das Beste" → Angebot mit Wertaufstellung → Preis → CTA. Die Overlays folgen dieser Reihenfolge und sind an **gesprochene Wörter** gekoppelt, nicht an Zeiten (siehe 5).

## 2 · Start-Hook (die ersten ~6 Sekunden)

1. **Große Zeile = Nutzen mit Zeitangabe, kleine Zeile darunter = Kontext.** Nie umgekehrt: Der Kunde wollte „ERFAHRE IN 1 MINUTE 45" groß und den erklärenden Satz klein darunter. Die Zahl ist das, was zum Dranbleiben zwingt.
2. **Live-Countdown statt statischer Zeit.** Die Zeit zählt pro Sekunde des *fertigen* Videos herunter (45, 44, 43 …), solange der Hook sichtbar ist. Ein Schritt = `NF = round(TEMPO × FPS)` Frames im Render (bei Tempo 1,1 und 30 fps: 33 Frames). Startwert = Pitch-Zeit im fertigen Video − Hook-Startzeit, gerundet. Feste Boxbreite über alle Schritte (breiteste Variante messen), sonst springt die Box. Nur der erste Schritt blendet ein (6 Frames), nur der letzte aus (8 Frames).
3. **Untertitel aus, solange der Hook sichtbar ist.** Zwei Textschichten gleichzeitig wirken überladen. Caption-Zeichnen im Frame-Loop für `H1F0 ≤ f < H1F1` überspringen.
4. **Größe:** Hook-Box max. 760 px breit bei 1280-px-Video, große Zeile 44 px, kleine 15 px. Die erste Fassung (große Box, 3 Zeilen) wurde als „viel zu groß" reklamiert. Bei Zweifel kleiner.
5. Position unten über dem Untertitelband (Boxunterkante y ≈ 586 bei 720p), nicht über dem Gesicht.

## 3 · Teaser und Rehook-Countdown

6. **Teaser** direkt vor dem Angebot („ACHTUNG / DAS BESTE KOMMT GLEICH"), ca. 4 s. Kunde: gut, beibehalten.
7. **Rehook-Countdown** 10 → 1 vor dem Angebotsmoment, je eine Videosekunde pro Zahl. Zusatz: **Der Countdown sagt nur „DAS BESTE KOMMT IN" + Zahl.** Kein Verweis auf den Inhalt des Angebots („VIP-WhatsApp-Gruppe …"): Der Reveal soll erst passieren, wenn der Sprecher es sagt. Zahl moderat (50 px, nicht 76 px), Box fest 250 px breit.
8. Der Countdown endet auf dem Anker-Wort des Angebots (Start − Lead 0,35 s), nicht irgendwo davor: `CD0 = anker − 10 × NF`. Assert, dass Teaser-Ende + Puffer < CD0.

## 4 · Wert-/Ticket-Karte (oben rechts)

9. Die Karte baut sich **zeilenweise zu den gesprochenen Bestandteilen** auf (Zeile erscheint ca. 0,15 s vor dem Wort). Danach: Gesamtwert **durchgestrichen**, optional Normalpreis **durchgestrichen**, dann der Aktionspreis groß. So liest man die Preisleiter ohne Rechnen.
10. Zeilen mit Zusatznutzen bekommen eine zweite Zeile in Akzentfarbe („mit Oli persönlich"). Das war der Kunden-Wunsch: das Mehrwert-Merkmal oben rechts mit anzeigen.
11. Karte endet am Satzende des Angebots (Anker nach dem letzten Preiswort), 8 Frames ausblenden.
12. **Preis wörtlich aus dem Sprechtext, nicht aus der Kundenschreibweise raten.** „2999" in der Nachricht = „29,90 €" (so gesprochen). Bei Zahlen ohne Komma im Briefing immer zurückfragen oder gegen die gesprochene Zahl prüfen.

## 5 · Overlay-Zeitpunkte aus Wort-Anker

13. Overlay-Zeiten kommen aus **Wort-Indizes** (`words.json`, Index des ersten Wortes der Einblendung) über die Plan-Segmente in die Ausgabezeit (`tO(i, offset)`), nicht aus Quellzeiten. Jede Schnittänderung verschiebt sie dann automatisch mit.
14. Beim Anker-Lookup mit `assert`, dass das Wort im Schnitt liegt (sonst liegt der Anker in einem entfernten Bereich). Whisper-Onset nach Pausen ist 0,1–0,4 s zu spät: Offset −0,15 s für Karten-Zeilen, −0,35 s für große Einblendungen.
15. **Zeitlabels im Hook** (z. B. „ab 1:45") aus dem Anker berechnen und durch das Tempo teilen (`label = ausgabezeit / TEMPO`), nie hartcodieren. Nach jeder Neuversion prüfen: stimmt die Zahl im Hook mit dem tatsächlichen Beginn des Pitches im fertigen Video?

## 6 · Varianten und Kürzen des Pitches

16. **Drei Längen anbieten**: ganz lang (komplett), mittellang (Standard), kompakt. Der Kunde entschied sich am Ende für zwei (ganz lang + mittellang). Ein Skriptlauf pro Variante, alle mit denselben Overlays (Anker aus Wort-Indizes machen das automatisch).
17. **Was beim Kürzen zuerst rausfliegt:** Wiederholungen („Wir geben wirklich Input"), reine Beteuerungen („das ist kein Scheiß jetzt, ich meine das total ernst"), Aufzählungen des Inhalts, wenn der Inhalt schon im Hook/Teaser versprochen ist, und Doppelversprechen („zwei Abende … Wissen mitnehmen und Inspiration …"). **Was bleibt:** Nutzen-Satz, Beleg/Referenz, Übergang zum Angebot, Angebot komplett, CTA.
18. Nach jedem Block-Cut den neuen Satzübergang vorlesen: Passt der Anschluss grammatisch und inhaltlich („… wie du es machst. Aber nachher geht es ans Umsetzen.")? Schnitt in echter Stille, Frame vor/nach ansehen.
19. Beim Kürzen ändert sich die Pitch-Zeit im Hook automatisch (Anker); trotzdem den ersten Hook-Wert gegenprüfen.

## 7 · Auflösung, Bitrate und Auslieferung (häufigste Fehlerquelle)

20. **Quellauflösung vor dem Versprechen messen** (`ffprobe`): Das Original war 1280×720 mit 3,4 Mbit/s. 1080p ist dann ein reines Hochskalieren (Lanczos + leichtes Unsharp), kein Mehr an Details. Dem Kunden das vor dem Final sagen, nicht danach.
21. **„Niedrige Qualität"-Reklamation = zuerst prüfen, welche Datei er geöffnet hat.** Eine 29-MB-Datei bei 1080p/3 min hat nur ~1,6 Mbit/s, also die Hälfte des 720p-Originals: sie sieht schlechter aus als das Original. Bitraten-Orientierung 1080p-Talking-Head: Vorschau ≥ 1,6 (nur Ansicht), Master ≥ 5 Mbit/s (≈ 130 MB für 3 min, ≈ 170 MB für 4 min).
22. **Master und Vorschau getrennt benennen** (`…_FINAL_1080p_master.mp4` vs. `VORSCHAU-klein_…`), im selben Ordner, damit nichts verwechselt wird.
23. **Zwischenformat verlustarm rendern**: Frame-Loop-Render mit hoher Bitrate (`--mb 350`, ≈ 12–14 Mbit/s bei 720p), erst der letzte Encode (Skalierung + Tempo + Ton) bestimmt die Endqualität. Nicht dreimal verlustbehaftet nacheinander kodieren.
24. **Große Dateien über die Geräte-Brücke:** Pro Datei max. ~30 MB, pro Aufruf max. 100 MB. Master in Teile ≤ 19 MB schneiden (`split -b 19000000 -d -a 2`, Endung `.p00`, `.p01` …), Teile in Batches ≤ 5 pro Commit-Aufruf, und eine `ZUSAMMENFUEGEN.bat` mitliefern (`copy /b teil.p00+teil.p01+… ziel.mp4`, Zeilenenden CRLF). Dem Kunden vorher sagen, dass er einmal doppelklicken muss. Zusammengefügte Datei nach dem Zusammenfügen kurz abspielen lassen.

## 8 · Render-Betrieb (Cloud-Container)

25. **Hintergrundjobs überleben das Ende des Antwort-Zugs nicht zuverlässig.** Nach „Turn beendet" waren in zwei Fällen alle Render-Prozesse weg. Während Rendern läuft: Zug offen halten und mit **einzelnen** `sleep ≤ 110 s`-Aufrufen pollen (Dateigröße der Ausgabe wächst). Mehrere parallele Sleep-Aufrufe in einem Block laufen gleichzeitig ab und bringen nichts.
26. Mehrere Varianten in **einem** Kettenskript nacheinander (`for n in …; do render; speed; done`) mit einem Logfile je Schritt (`runr.log`). Zwei Kerne: ca. 10–13 Min pro 3–4-Minuten-Render + 5–9 Min Export.
27. Nach jedem fertigen Video sofort QC (LUFS/TP, Freeze, A/V-Dauer) + 4-Frame-Streifen (Hook, Rehook, Karte, normaler Untertitel) ansehen und **gleich ausliefern**, nicht bis alle fertig sind.

## 9 · QC-Checkliste für Verkaufsvideos (zusätzlich zu `qc-parameter.md`)

- Hook: Zeilenreihenfolge, Countdown-Startwert = tatsächlicher Pitch-Beginn, keine Untertitel im Hook, Box schmal.
- Teaser und Rehook: nur das Versprechen, nichts vom Angebot vorweggenommen, Zahl nicht zu groß.
- Karte: jede Zeile erscheint beim gesprochenen Wort, durchgestrichene Werte lesbar, Endpreis = gesprochener Preis.
- Schnitt: kein Wort fehlt, Frame vor/nach jedem Block-Cut gesehen, kein Standbild am Ende.
- Technik: −14 ± 0,5 LUFS, TP ≤ −1,2, Freeze 0, A/V < 0,1 s (je Variante).
- Auslieferung: Master und Vorschau getrennt, Bitrate/Auflösung dem Kunden ehrlich genannt.

## 10 · Typische Kundenreaktionen und die Antwort darauf

| Reaktion | Ursache | Antwort |
|---|---|---|
| „Hook viel zu groß" | Box und Schrift an Reel-Format orientiert, nicht ans Danke-Video | kleine Box, große Zeile nur für die Zahl |
| „Das ist doch niedrige Qualität" | Vorschau-Datei statt Master geöffnet | Bitrate belegen, Master benennen, Original-Spezifikation zeigen |
| „Erwähne die Gruppe noch nicht" | Rehook verrät das Angebot | Reveal nur im gesprochenen Moment/Karte |
| „Ein dritte Version mit weniger Pitch" | Pitch dem Kunden zu lang | Block-Cuts nach 6 · 17, Satzübergänge prüfen |
