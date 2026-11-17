# Untertitel „Clean-Style“ (Standard für High-Production-Reels)

Abgenommen von Christoph am 17.11.2026 (Pilot Oliver Geisselhart, A01 v3/v4): „Die Untertitel sind Hammer, so will ich die.“
Das ist der **Default-Untertitelstil für 9:16-Reels** und hat Vorrang vor den Karaoke-/Chip-Presets aus `captions.md`, sofern der Kunde nicht ausdrücklich Chip-Karaoke will. Er gilt für jeden Kunden — nur die CI-Werte (Font, Akzentfarbe) kommen aus der `kunden-config.yaml`. Layout, Größen, Schatten, Gruppierung und Platzierungslogik bleiben unverändert.

## Spezifikation (9:16, 1080×1920)

| Eigenschaft | Wert |
|---|---|
| Schrift | Kunden-Font, Normalschnitt = **Medium** (kein Bold im Fließtext), Größe **52 px** |
| Schlüsselwort | max. **1 pro Gruppe**, Schnitt **BoldItalic** in Akzentfarbe (Oli: Orange 255,128,34) |
| Textfarbe | Weiß, **keine Kontur**, kein Chip, kein Hintergrundkasten |
| Schatten | weicher Doppelschatten: Gauß-Blur 8, Alpha ~200, dy 4, plus enger Kontaktschatten Blur ~1,6 |
| Gruppierung | **2–3 Wörter**, max. 20 Zeichen pro Gruppe, Umbruch an Satzgrenzen/Atempausen |
| Animation | Einblenden 0,12 s mit 10 px Aufwärtsbewegung, kein Pop, kein Overshoot, kein wanderndes Highlight |
| Timing | Anzeige 0,02 s vor Wort-Onset; Gruppenwechsel lückenlos |
| Lesbarkeits-Verlauf | dunkler Bodenverlauf über das Video, Alpha 0→105/255 von y=880 bis 1440 (Kurve u^1.4) — trägt weiße Schrift auf weißem Hemd |
| Schlüsselwörter | aus dem Marken-Profil (Kernbegriffe des Kunden), nie willkürlich |

## Platzierung (Pflicht, face-aware)

Untertitel liegen **nie im Gesicht** (Kinn, Mund). Pro Shot messen, nicht schätzen:

1. Gesichtserkennung auf Frames des fertigen Bildausschnitts (4 fps), YuNet (`cv2.FaceDetectorYN`, `face_detection_yunet_2023mar.onnx` aus opencv_zoo; Haar-Cascades fehlen in cv2 5.x). Koordinaten in Ausgabebild-Pixel umrechnen — inklusive Push-/Zoom-Verlauf des Shots.
2. Standard-y = 1190 (≈ 62 %). Liegt das Kinn tiefer: y = **Kinn + 95 px**.
3. Ergibt das y > 1540 (Plattform-UI unten): Untertitel **über den Kopf** (y = Oberkante Kopf − 95, mind. 330), sonst 1540.
4. Wert pro Shot festhalten und für den ganzen Shot konstant lassen (kein Wandern).
5. Webinar-Layout (Sprecher oben, Visualisierung unten): Untertitel an die Naht (y ≈ 905), Fallback 1005.
6. Kein Gesicht erkannt (Profil, Hand vor dem Gesicht): Default-y und im QC-Frame prüfen.

Abnahme-QC nach dem Render: Frames aus dem **fertigen** Video ziehen, Gesicht erneut erkennen, Untertitel-Band (±42 px um y) gegen die Gesichts-Box prüfen → 0 Überlappungen. Erkennungen im unteren Layout-Teil (Grafik) sind Fehlalarme.

## Hook im selben Stil

Hook-Zeile: Bold 70 / Medium 62, Schlüsselwort BoldItalic in Akzent, y = max(300, min(420, Kopf-Oberkante − 190)). Gleiche Schattenlogik. **Keine Einblendung von Präsentationsfolien** — Inhalte werden als eigene, ruhige Animation nachgebaut (Glas-Karten, Kurve, Treppe), nie als Screenshot.

## Bauchbinde

Standardmäßig **keine** Bauchbinde (Kunden-Feedback 17.11.2026). Nur wenn die Config `bauchbinde: true` setzt.

## CI-Übertragung auf andere Kunden

Aus der Kunden-Config werden nur `font_family`, `accent_color` und optional `text_color` gezogen. Der Font braucht Medium/Regular und einen kursiven Fettschnitt; fehlt Kursiv, Schlüsselwort stattdessen Bold in Akzentfarbe. Fehlt ein Schnitt, laut scheitern — kein stiller Fallback.
