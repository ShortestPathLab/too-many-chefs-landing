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
- `src/styles/global.css`: Tailwind entry point and global styles.

## Deploy

`.github/workflows/deploy.yml` builds the site and publishes `dist/` to GitHub
Pages on every push to `main`. In the repository settings, set the Pages source
to GitHub Actions.

The build reads the site address from `SITE_URL`. The workflow uses the
`SITE_URL` repository variable if one is set, and the default Pages address
otherwise. Local builds without `SITE_URL` leave out canonical URLs and the
sitemap.
