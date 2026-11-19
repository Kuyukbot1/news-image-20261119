[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Kuyukbot1/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Kuyukbot1/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

# Thursday 19 November 2026: 42 stories, 6 continents, one front page and a map

An entry for the [make.fun bounty](https://make.fun/bounty/news-image-20261119).

One 1024×1024 image summing up Thursday 19 November 2026 — 42 verified stories
across 6 continents, drawn as a newspaper front page:

- **Masthead** — "Thursday 19 November 2026" over "42 stories · 6 continents · all from Thursday".
- **13 illustrated feature cards** — the first-ever Trump–Xi–Putin trilateral
  summit in Shenzhen as APEC opens; Iran says three tankers hit mines east of
  Hormuz; GTA VI launches worldwide; Anthropic prices a record $83 IPO and
  debuts on Nasdaq; the World Court rules on the Rohingya genocide case; a Van
  Gogh sells for a record $190.4m; Cyclone Akvan bears down on India's east
  coast; Hegseth's surprise US–Venezuela defence pact; Jeffries nominated as
  the first Black House Speaker; Israeli tanks cross the Gaza ceasefire line;
  Scotland lose in Greece but stay a win from the World Cup; a magnitude 5.7
  quake in Kumamoto; Voyager 1 passes one light-day from Earth.
- **"Where it happened"** — a world map with numbered pins matching the cards.
- **"Also on Thursday 19 November"** — 29 further stories, country-first.
- **Footer** — every story happened or was first reported on Thursday
  19 November 2026; disputed claims are attributed. Sources: AP, Reuters,
  AFP, BBC, Al Jazeera, UN News. Original drawings.

## How it is built

`draw.py` (Python 3 + Pillow, DejaVu Serif/Sans) draws `entry.png` from the
verified stories in `../RESEARCH_19NOV.md`; re-running it reproduces the
image byte-identically. `main.ts` (Node 22, standard library only) copies
`entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`.

## Verification

- `entry.png` — 1024×1024, 207,245 bytes (≤1 MiB), sha256
  `08e8a4202f354a6d58cf11266978acecee4ac58f38b953055da9fea781108469`
- `draw.py` re-run reproduces the identical sha256.
- `main.ts` run twice writes byte-identical output (same sha256).
- Viewed at full size and at 300 px: all text legible and unclipped, no
  overlaps, masthead date is the biggest element.
