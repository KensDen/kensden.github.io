# kensden.github.io

My personal site: a casually technical "about me," built as static HTML pages and served on GitHub Pages.

**→ Live at [kensden.github.io](https://kensden.github.io)**

Securing Agentic AI with Zero Trust · Army Major (Ret.) · maker and dad.

## About this repo

- `index.html`: the homepage (HTML and CSS, no framework, no build step, no JavaScript)
- The other `.html` files: essays, the Claude cert study guide and drill, and the 404 page
- `fonts/`: self-hosted JetBrains Mono and Space Grotesk (latin subsets, SIL OFL 1.1, see `fonts/OFL.txt`)
- `social-card-v3.png`: the homepage's link-preview image (the two cert pages and every dispatch have their own cards: `social-card-drill.png`, `social-card-study-guide.png`, `social-card-10-cent-dreams.jpg`, `social-card-multiverse.jpg`, `social-card-batman.jpg`, `social-card-seat-at-the-table.jpg`, `social-card-measuring-security.jpg` and `social-card-sanctuary.jpg`)
- `.nojekyll`: tells GitHub Pages to serve the static HTML as-is
- `tools/quotes.py`: the prose quote check. `python3 tools/quotes.py` fails if any page has a straight quote in its prose (code, attributes, scripts and styles are left alone); `--fix` curls them and `--list` shows each one. Run it before every push.
- `tools/social_card.py`: builds the four dispatch cards with a title on them (Batman, Seat at the Table, Measuring Security, Sanctuary Protocol) from each dispatch's own image, in the site's fonts, at 1200x630 and under 300 KB. Needs Google Chrome and macOS `sips`.

## Find me

- LinkedIn: [kendallconnell](https://www.linkedin.com/in/kendallconnell)
- Mastodon: [@KenDC@infosec.exchange](https://infosec.exchange/@KenDC)
