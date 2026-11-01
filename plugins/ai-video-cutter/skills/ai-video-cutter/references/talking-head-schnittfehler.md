# Talking-Head-Schnittfehler und ihre Gegenmaßnahmen

Gesammelt aus den Feedbackrunden Oktober/November 2026 (Oliver-Geisselhart-Reels und Danke-Seiten-Videos). Jede Regel steht hier, weil ihre Verletzung vom Kunden gehört oder gesehen wurde. **Pflichtlektüre vor jedem Talking-Head-Schnitt**, zusätzlich zu `schnitt-regeln.md`.

## 1 · Schnittpunkte

1. **Nie auf Whisper-Wortgrenzen schneiden.** Whisper-Onsets nach Pausen kommen oft 0,1–0,4 s zu spät („Aber" 146,32 statt real ≈ 146,0; „Normalpreis" angeschnitten), Wortenden sind unzuverlässig. Schnittpunkte kommen aus der Energiekurve (10-ms-Hop, Stille < −46 dB), nicht aus dem Transkript.
2. **Schnitt-Aus** (nach einem Wort): erste echte Stille nach dem Wortende, 0,22 s Nachhall stehen lassen. **Schnitt-Ein** (vor einem Wort): in der letzten Stille vor dem Einsatz, 0,12–0,25 s Vorlauf (Plosive beginnen bis 0,2 s vor dem Whisper-Onset). Liegt keine Stille an der Stelle (< 0,07 s), ist das kein erlaubtes Schnittfenster.
3. **Satzton prüfen (f0-Verlauf).** Vor einem Schnitt die Tonhöhe vor und nach der Schnittstelle messen (Autokorrelation reicht): Satzende = tief und fallend, Satzmitte = schwebend/steigend. Wer mitten in einem schwebenden Ton schneidet, erzeugt einen „unsauberen" Übergang, auch wenn die Energie passt. Im Zweifel den Schnitt hinter den Satzabschluss oder hinter einen ganzen Satz legen.
4. **Füllton (äh) entfernen nur an den exakten Grenzen des stimmhaften Laufs.** Wird ein „äh" gekürzt und die Nachbarwörter verändern sich akustisch (Whisper hört „der geilsten" statt „zur geilsten"), den Füllton lieber drin lassen. Nach dem Entfernen die Pause bewusst gestalten (ca. 0,3–0,4 s statt 0,13 s), sonst wirkt der Satzübergang abrupt.
5. **Störgeräusche im Übergang** (Vogel, Klick, Lippenschmatzen): Übergang nicht nur auf Energie, sondern auf Breitband-Anteil prüfen. Zweiten Kandidaten in einer anderen Stille suchen.
6. **Zeitangaben des Kunden** beziehen sich auf den Player des fertigen Videos. Immer über die Plan-Segmente auf Quellzeit zurückrechnen und dem Kunden „Ausgabe 0:29 = Quelle 117,2 s" zurückspiegeln, damit beide dieselbe Stelle meinen. Sagt der Kunde „bei dem Frame, wo du den Screenshot geschickt hast": den Frame per Untertitelwort + Zeit identifizieren und dort exakt schneiden.

## 2 · Enden von Videos

7. **Das Ende ist der natürliche Satzabschluss + Ausklang**, nie mitten in der Betonung. Folgt nach dem letzten Wort noch Stimme (Folgesatz, Nachsatz), gehört sie ins Video. Beschwerde „am Ende komisch beendet" bedeutet fast immer: Folgesatz fehlt.
8. **Kein Standbild und kein Heranzoomen am Ende.** Das Video läuft einfach weiter (Ruhebild 0,5–1,0 s nach dem letzten Wort), Ton blendet per Cosinus-Fade (0,5 s) aus. Hold-Frames mit Zoom wirken wie ein Fehler.
9. **Lieber eine Sekunde früher enden als zu spät**, wenn danach Atmen/Nebengeräusche oder eine neue Ansatzbewegung kommen. Frame des letzten Bildes ansehen (Mund geschlossen, Blick ruhig).
10. **Kundenstimmen und Zitate**: Anfang UND Ende des Zitats prüfen. Wirkt eine Kundenstimme „abgeschnitten", fehlt ein Satzanfang oder ein Ausklang. Zitat vollständig mitnehmen, auch wenn die Ziellänge dadurch um 1–2 s wächst.
11. **Mimik nach dem letzten Wort**: Macht der Sprecher nach dem Wort noch eine Geste oder einen Gesichtsausdruck, der etwas ankündigt („komisches Gesicht", Ansatz zu einem weiteren Satz), darf der Cut nicht davor liegen, es sei denn, der Satz selbst soll bewusst enden. Dann zwei Varianten liefern: (A) Cut direkt nach dem Wort, (B) mit Folgesatz.

## 3 · Untertitel

12. **Vollständigkeit**: Anzahl der angezeigten Wörter = Anzahl der gesprochenen Wörter im Plan (abzüglich geklebter Bindestrich-Tokens). Wörter dürfen nie verschwinden, weil ein Onset-Refinement sie vor den Segmentbeginn schiebt. Refinement nur ≤ 0,45 s zurück und nie außerhalb des Segmentfensters; sonst fallback auf den Whisper-Onset.
13. **Glossar-Gate** vor jedem Render: bekannte Whisper-Fehler des Kunden ersetzen und prüfen („Onkel Oli" → „Olli", „Trigger-Deck-Kiste" → „Trick an der Kiste", „Durchstarteticket" → „Durchstarter-Ticket", „Webinare" → „Webinar", „tostenlos" → „kostenlos", „Chunk" → „Junk", „Medias Race" → „Medias Res", „Gaiselhardt" → „Geisselhart"). Mehrdeutige Erkennungen (Eigennamen, Fachbegriffe) immer gegen den Satzsinn lesen. (Kundenspezifische Einträge gehören in die `kunden-config.yaml`, nicht ins Plugin.)
14. **Größe an den Player anpassen**, nicht an das Quellvideo: Bei 1280×720, das im Web nur ca. 640 px breit läuft, wirkt Schriftgröße 44 zu groß. Standard dort: Montserrat 700, Größe 32, Boxhöhe 1,5 × Schrift, Box bei y ≈ 598–646 (über der Player-Leiste), Zeilenbreite max. 860 px.
15. **Hook-Overlay nie so breit wie das Video.** Breite begrenzen (bei 1280 Breite ca. 700–760 px), lieber eine Zeile mehr. Position nicht über dem Gesicht.

## 4 · Audio

16. **Loudness/True Peak am fertigen MP4 messen, nicht an der WAV.** AAC-Encoding legt nach einem Limiter 2–3 dB Peak drauf (gemessen: WAV −3,2 dB, MP4 −0,1 dB). Rezept, das hält (−14,2 LUFS, TP −1,8 bis −2,2): `alimiter=limit=0.35:attack=2:release=40` → `loudnorm=I=-13.8:TP=-3:LRA=11` → `alimiter=limit=0.55:attack=2:release=40`, AAC 160 kbit/s. Nach dem Encode messen, bei TP > −1,2 Kette strenger machen.
17. **Tempoänderung (1,05 / 1,1)** per `atempo` (Tonhöhe bleibt) und `setpts=PTS/f,fps=30`; Untertitel laufen automatisch mit, wenn sie eingebrannt sind. Danach Pegel neu normalisieren (Regel 16) und A/V-Dauer messen.
18. **A/V-Dauer**: bei jeder Version messen (< 0,1 s). Hold-Frame-Enden bekommen `tpad=stop_mode=clone`, damit das Video nicht kürzer als der Ton ist. (Kein Hold-Frame-Zoom, siehe Regel 8.)

## 5 · Bild

19. **Farbgrading und Zahnaufhellung auf dem kompletten Quellvideo einmal rechnen**, danach Segmente schneiden. So bleibt die Farbe zwischen den Segmenten stabil. Vorher/Nachher-Crop der Zähne ansehen.
20. **Zoom-Animation für kurze Varianten**: gerade Segmente langsam hinein (1,00 → 1,08), ungerade Segmente heraus (1,14 → 1,06). Der Sprung an der Segmentgrenze (≈ 6 %) kaschiert den Jump-Cut. Mit `warpAffine` um (640, 330) skalieren, Rand mit `BORDER_REPLICATE`.

## 6 · Prozess

21. **Messen vor Bauen**: Stelle messen (Energie, f0, Whisper-Fenster), Plan zeigen, dann rendern. Nach dem Rendern Whisper über das FERTIGE Audio laufen lassen und gegen den Plan prüfen (fehlende/angeschnittene Wörter).
22. **Wenn dasselbe Reel zum zweiten Mal wegen derselben Abschneidung reklamiert wird: komplett neu bauen**, nicht den alten Plan flicken. Erst die Ursache finden (Segmentgrenze, Refinement, Fade), dann neu planen.
23. **Renderlast**: 2-Kern-Server, ein 4-Minuten-Render braucht 6–25 Minuten. Mehrere Aufträge nacheinander in einem Hintergrund-Skript starten (`setsid -f nohup`), nie `pkill -f`/`pgrep -f` mit Mustern verwenden, die den eigenen Befehl treffen (beendet die Shell); Prozesse per PID beenden. Fertige Dateien sofort ausliefern, nicht am Ende bündeln.
24. **Lieferung**: jede Version in den Kundenordner (nie überschreiben, Version hochzählen), Anhangskarte im Chat, klickbare `computer://`-Links, am Ende ein Satz: „Das hat das System gelernt …".
