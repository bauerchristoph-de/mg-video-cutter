# Clip-Montage mit Musik — der zweite Auftragstyp

Der Standardfall des Video-Cutters ist ein Sprecher (Talking-Head, Webinar, Interview):
Transkript, Karaoke, Emphasis. Der zweite Auftragstyp hat **keine Sprache**: mehrere kurze
Handy-Clips, ein Musikstück, kurze Texteinblendungen — das Format, das auf Instagram und
TikTok als „Trend-Reel" läuft („Wer kommt wann zum Training?", „POV: Montagmorgen im
Büro", „Unser Team in 20 Sekunden"). Meist bringt der Kunde ein Vorlagen-Video mit
(„so wie das hier, nur für uns").

Alles, was hier steht, ist an einem realen Auftrag in neun Freigaberunden entstanden.
Jede Regel hat eine Korrektur des Kunden hinter sich.

## Woran man den Auftragstyp erkennt

- Material: 5–15 Clips à 4–12 s, Handy, hochkant, ohne Interview-Ton.
- Vorlage: ein fremdes Reel/TikTok mit Trendsound.
- Wunsch: „schlicht", „wie in Instagram bearbeitet", „nicht wie ein Werbeclip".

Dann gilt **dieser Ablauf, nicht der Talking-Head-Ablauf.** Kein Transkript, keine
Karaoke, keine Emphasis, keine SFX. Werkzeuge: `scripts/montage_beatgrid.py`,
`scripts/montage_build.py`, `scripts/montage_render.py`.

## Der Look: „in Instagram getippt", nicht „vom Tool gebaut"

Die häufigste Korrektur in diesem Format lautet **„zu groß, zu bunt, zu viel"**. Was in
einem Projektfilm richtig ist (Chips, Panels, Titelkarten in CI-Farbe), wirkt hier wie
Werbung. Der Kunde will User-Generated-Content-Optik:

| Element | Regel | Wert |
|---|---|---|
| Text | weiß, ein Font (Kunden-Font oder Montserrat), **kein Kasten** | Bauchbinde SemiBold 54 px, Kommentar Medium 34 px, Titel ExtraBold 52 px |
| Lesbarkeit auf hellem Grund | weicher dunkler Glow + Schlagschatten hinter dem Text — nie ein Rechteck | Glow α≈110–150, Radius 22–26; Schatten α≈170–190, Versatz +2/+4 px |
| Hervorhebung | **genau ein** Wort im Titel in der Akzentfarbe | z. B. „Wer kommt **wann** zum Training?" |
| Titel-Position | direkt **über** der ersten Bauchbinde (unteres Drittel), nicht oben | y ≈ 1130 bei 1080×1920 |
| Bauchbinde | „Name – HH:MM Uhr", darunter optional ein Kommentar | y ≈ 1290, lange Namen automatisch kleiner (max. 940 px breit) |
| Kommentar | sachlich, aus echten Fakten, **keine Gags** | „(musste noch bei der Zweiten trainieren)" ja — „(Banane first)" nein |
| Bewegung | Push-in 100 → 105 % je Clip, harte Schnitte, Pop-in der Texte 3 Frames | kein Fade am Ende — das Reel loopt |
| Grade | Innenraum-Handyvideo heller: Schatten anheben, etwas Sättigung, leicht schärfen | `curves 0.22→0.30, 0.55→0.63` · `eq contrast 1.05 sat 1.14 gamma 1.04` · `unsharp 5:5:0.4` |

**Warum der Titel unten steht:** Ein Kasten oben verdeckt Köpfe (Korrektur: „schneidet
dem Coach den Kopf ab"), und das Thumbnail zeigt das Thema nur, wenn Titel und erste
Bauchbinde im ersten Frame zusammen sichtbar sind. Zwei Zeilen, schlank, kein Kasten.

## Tempo: auf dem Beat, kürzer als man denkt

- Beat-Raster der Musik messen (`montage_beatgrid.py beats`), Clips bekommen **Beats, keine
  Sekunden**: 3 Beats je Clip ohne Kommentar (~1,8 s bei 100 BPM), 4 Beats mit Kommentar,
  Finale 6–7 Beats. Gesamt 20–25 s.
- Segment = die **letzten** N Sekunden eines Clips (die Person kommt auf die Kamera zu);
  Ausnahme per `start`, wenn der Clip am Anfang das Bessere hat.
- Erste Fassung war 42 s („zu lang"), zweite 28 s, freigegeben 22 s. Im Zweifel kürzer.

## Musik: das Original, ab Frame 0, bis zum letzten Frame

1. **Nie den Ton aus dem Vorlagen-Video verwenden.** Er ist komprimiert und enthält
   Fremdstimmen. Der Kunde liefert das Original (Audio-Datei oder YouTube-Audio);
   `montage_beatgrid.py align` findet per Kreuzkorrelation die Liedstelle, die die
   Vorlage benutzt (Versatz auf ±5 ms).
2. **Musik ab Frame 0 auf vollem Pegel.** Der Offset liegt auf dem Beat-Einsatz, nie
   davor — ein leises Intro hört der Kunde als „dreht langsam hoch". Damit fällt manchmal
   die Idee weg, den Hook exakt aufs Finale zu legen; dem Kunden ist der Pegel wichtiger.
   Beides gleichzeitig versprechen geht nicht.
3. **Musik bis zum letzten Frame, kein Fade.** Der Ton muss exakt so lang sein wie das
   Bild — `montage_render.py` prüft das und `qc.py` hat das A/V-Gate. Siehe die Falle in
   `audio.md` („loudnorm im Filtergraph schneidet das Ende ab").
4. **Originalton bleibt hörbar:** Ambiente (Schritte, Türen, Stimmen) auf −24 LUFS unter
   der Musik (−16,5 LUFS); danach linear auf −14 LUFS gemastert wie jedes Video (`audio.md`). Ganz stumm wirkt es wie ein Werbespot.
5. Lizenz: Für Kundenkonten, die das Video selbst posten, entscheidet der Kunde, ob der
   Song eingebrannt wird oder ob er das Video stumm hochlädt und den Sound in der App
   wählt (Sound-Tag = Reichweite, kein Copyright-Risiko). Einmal anbieten, nicht wiederholen.

## Ablauf (kurz, weil das Format kurz ist)

1. Briefing: Vorlage, Clip-Ordner, Liste „wer/was/wann" vom Kunden, Musik-Original.
   Spitznamen/Namen **nur** vom Kunden, nie erfinden; unklare Namen aus Sprachnachrichten
   gegen eine schriftliche Quelle prüfen, bevor sie auf einen Frame kommen.
2. `montage_beatgrid.py beats <musik>` → `beats.npy`; bei Vorlage: `align`.
3. `montage-plan.json` aus `scripts/montage-plan.example.json`: Slides, Texte, Beats je
   Slide → `montage_beatgrid.py plan` schreibt Dauern und Offset.
4. `montage_build.py --config kunden-config.yaml --plan montage-plan.json` → Overlays.
5. `montage_render.py --plan montage-plan.json` → Master + Web-Version + QC-Zeile.
6. Framesheet (ein Frame je Slide) mitliefern; Kunde prüft auf dem Handy.
7. Jede Version als neue Nummer, Feedback als Kunden-Learning sichern (Schritt 8 der SKILL.md).

## Typische Feedback-Kaskade (damit sie beim nächsten Kunden nicht wieder neun Runden kostet)

| Der Kunde sagt | Ursache | Vorab richtig machen |
|---|---|---|
| „Text viel zu groß" | Projektfilm-Größen übernommen | Größen aus der Tabelle oben |
| „Nicht so krass in Farbe, basic und schlicht" | CI-Farbe als Textfarbe | weiß, ein Akzentwort |
| „Kasten verdeckt den Kopf" | Titelbox oben | Titel über der ersten Bauchbinde, Glow statt Kasten |
| „Text kaum zu lesen" | weiß ohne Glow vor Glastür/Tageslicht | Glow + Schatten, Kontrast am hellsten Frame prüfen |
| „Clips schneller" | Sekunden statt Beats | 3 Beats je Clip |
| „Musik dreht langsam hoch" | Offset im Intro | Offset = Beat-Einsatz |
| „Musik endet zu früh" | Ton kürzer als Bild (loudnorm-Falle) oder Fade | Stem-Mix, kein Fade, A/V-Dauer prüfen |
| „Man hört keine Stimmen" | Ambiente zu leise (−30) | −24 LUFS |
| „Da sind fremde Stimmen in der Musik" | Ton aus dem Vorlagen-Video | Original-Song + align |
| „Kommentare zu affig" | eigene Gags | nur Fakten vom Kunden |
