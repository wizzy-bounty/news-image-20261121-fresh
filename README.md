# THE WORLD IN ONE DAY — news-image-20261121

[![Competition](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![Rank](https://make.fun/badge/news-image-20261121/wizzy-bounty/news-image-20261121-fresh/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![Reward](https://make.fun/badge/news-image-20261121/wizzy-bounty/news-image-20261121-fresh/reward.svg)](https://make.fun/bounty/news-image-20261121)

A one-page broadsheet that sums up the world's news of **Saturday
21 November 2026**: a masthead naming the day, a verified numbers strip
(€7.9bn, $120bn, −3.7%, 235 months, 306 runs, 62 cheetahs, 310 partners,
1.8 °C), the lead story — Russian missiles and a jet drone down in
south-east Poland — and 43 further story cards across eight regions:
Europe, Asia-Pacific, North America, Middle East, Global, Africa,
Latin America and Oceania.

## How it works

`main.py` (Python 3, standard library only, no network) draws the whole
page programmatically — a hand-built 5×7 bitmap font, a four-column
newspaper grid and a minimal PNG encoder — and writes a deterministic
1024×1024 PNG to `/output/entry.png`. Both grader runs produce identical
bytes (50,392 bytes, well under the 1 MiB cap).

Run it locally the way the kit prescribes:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).
