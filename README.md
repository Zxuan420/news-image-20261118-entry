# news-image-20261118-entry

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Zxuan420/news-image-20261118-entry/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Zxuan420/news-image-20261118-entry/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A pure Python (standard library only) program that draws one 1024x1024 image summing up the world's news of Wednesday 18 November 2026: US strikes on Iran and Iran's drone retaliation, the Kerch Bridge hit, the APEC summit opening in Shenzhen, Peltola's Alaska Senate win, the US losing measles-free status, and Voyager 1 reaching one light-day from Earth — plus the day's other big stories in a footer strip. Flat newspaper-front-page style with a small embedded bitmap font, fully deterministic.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Details
- Canvas: 1024x1024 RGB PNG
- Zero external dependencies (uses standard library `struct`, `zlib`, `math`, `os`).
- Fully deterministic: identical byte output across runs.
- No network.

---

<sub>Entered on [make.fun](https://make.fun/?ref=rkyytyv2&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
