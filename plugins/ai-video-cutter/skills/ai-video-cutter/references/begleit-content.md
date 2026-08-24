# Begleit-Content — optionale End-Outputs zum fertigen Video

Nach der Video-Abnahme (nie vorher — Text zu einem Video, das sich noch ändert, ist doppelte Arbeit) liefern, was in der `kunden-config.yaml` unter `begleit_content` aktiviert ist. Alles entsteht aus Material, das ohnehin vorliegt: Transkript, Schnittplan, Kernbotschaft aus dem Briefing.

## Grundgesetz: Bestehende Kundenkanäle, Kundensprache, Kanalsprache

- **Nur für Kanäle schreiben, die der Kunde wirklich bespielt** (`kanaele.plattformen` in der Config, im Setup erhoben). Keine Vorrats-Captions für Kanäle ohne Account.
- **Kundensprache:** Das `marken-profil.md` (angelernte Brand Voice mit Belegen — Wortschatz, No-Go-Wörter, Hook-/CTA-Muster je Account) ist verbindlich; `wording_notizen` in der Config ist nur die Kurzfassung. Die Caption muss klingen, als hätte sie der Kunde selbst geschrieben. Bei Unsicherheit: 2–3 aktuelle Posts des Kunden AUF DIESEM Kanal nachlesen, bevor geschrieben wird.
- **Kanalsprache:** Jeder Kanal hat eigene Konventionen — und der Kunde hat auf jedem Kanal einen eigenen Ton (LinkedIn oft förmlicher als Instagram, auch beim selben Absender). Beides gilt gleichzeitig: die Konvention des Kanals UND wie DIESER Kunde dort schreibt. Wenn der Kunde die Kanal-Konvention bewusst bricht (z. B. lange Instagram-Captions, die funktionieren), gewinnt der Kunde — als kundenspezifisches Learning festhalten.

## 1 · Caption (je Kanal eine eigene Fassung, nie eine für alle)

Aufbau: **Hook-Zeile** (verstärkt die erste Video-Aussage, wiederholt sie nicht wörtlich) → 2–4 kurze Zeilen Substanz (Kernaussage des Videos in Kunden-Wording) → **CTA** (aus den Standard-CTAs der Config oder dem Video-CTA) → Hashtags nach Config.

Kanal-Konventionen als Ausgangspunkt (Kunden-Ton auf dem Kanal geht vor):
- **Instagram/TikTok:** kurz, Zeilenumbrüche als Rhythmus, Hook vor dem „mehr"-Fold (~125 Zeichen), Hashtags am Ende.
- **LinkedIn:** erste 2 Zeilen entscheiden (Fold), Substanz darf länger sein, max. 3–5 Hashtags, keine Hashtag-Wolke.
- **YouTube (Beschreibung):** erster Satz = Suchintention, dann Kontext, Links, Kapitel falls sinnvoll.
- **Facebook:** wie Instagram, aber Hashtags sparsamer.

## 2 · Hook-/Titel-Varianten

3 Titel-Optionen für YouTube/Shorts bzw. Thumbnail-Text: je eine Variante Nutzen, Neugier, Zahl. Aus der stärksten Aussage des Transkripts, nicht erfunden.

## 3 · Post-Text-Kurzfassung

Die Kernaussage des Videos als eigenständiger Text-Post (für Kunden, die Video + Textpost parallel spielen). Nur wenn in Config aktiviert.

## Regeln

- Text entsteht aus dem Transkript — Behauptungen, die im Video nicht vorkommen, haben in der Caption nichts verloren.
- Lieferung als eine Markdown-Datei `fertig/<video>_begleitcontent.md` neben dem Video, pro Kanal ein Abschnitt zum Direkt-Kopieren.
- Kein eigener Freigabe-Loop: einmal mitliefern; Wording-Feedback ist fast immer kundenspezifisch → kunden-learnings.md bzw. `wording_notizen` in der Config nachschärfen.
