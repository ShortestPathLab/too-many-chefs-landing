# Too Many Chefs landing site

The landing site for [Too Many Chefs](https://github.com/ShortestPathLab/too-many-chefs).
It introduces the project and links to its resources. Built with Astro and
Tailwind CSS.

## Develop

Install [Bun](https://bun.sh), then run:

```bash
bun install
bun run dev
```

The site is served at http://localhost:4321.

| Command           | What it does                       |
| ----------------- | ---------------------------------- |
| `bun run dev`     | Start the dev server               |
| `bun run build`   | Build the static site into `dist/` |
| `bun run preview` | Serve the built site locally       |
| `bun run check`   | Type-check the project             |
| `bun run format`  | Format the source with Prettier    |

## Layout

- `src/config.ts`: site title, description, navigation and external links.
- `src/layouts/Layout.astro`: the page shell shared by every page.
- `src/components/`: header and footer.
- `src/pages/`: one file per page (`index`, `resources`, `creators`, `404`).
- `src/styles/global.css`: Tailwind entry point, colours, fonts and the tile
  styles.
- `scripts/record-hero.py`: records the gameplay montage on the home page.

## Gameplay montage

The home page plays `public/videos/hero.mp4` (or `hero.webm`). To record it
again after the simulator changes, run:

```bash
uv run scripts/record-hero.py --simulator ../overcooked-2
```

The script runs the simulator's default controller on the levels listed at the
top of the file, replays each run in headless Chromium with the panels hidden,
and joins a six-second clip from each into the video and its poster image. It
needs uv, ffmpeg and a Chromium installed for Playwright. Edit `LEVELS` in the
script to change which kitchens appear.

## Deploy

The site is published at https://toomanychefs.pathfinding.ai through GitHub
Pages. `.github/workflows/deploy.yml` builds the site and publishes `dist/` on
every push to `main`. It can also be run by hand from the Actions tab.

In the repository settings, Pages uses GitHub Actions as its source and
`toomanychefs.pathfinding.ai` as its custom domain. `public/CNAME` records the
domain in the source. The domain's DNS needs a `CNAME` record for
`toomanychefs` pointing to `shortestpathlab.github.io`.

Canonical links and the sitemap use the production address. To build for
another address, set `SITE_URL` locally or as a repository variable.
