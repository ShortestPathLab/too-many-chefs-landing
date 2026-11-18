import sitemap from "@astrojs/sitemap";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "astro/config";

// The production address, also recorded in public/CNAME. Set SITE_URL to
// build for another address.
const site = process.env.SITE_URL || "https://toomanychefs.pathfinding.ai";

export default defineConfig({
  site,
  integrations: [sitemap()],
  vite: { plugins: [tailwindcss()] },
});
