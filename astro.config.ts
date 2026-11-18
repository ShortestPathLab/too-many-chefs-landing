import sitemap from "@astrojs/sitemap";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "astro/config";

// Set SITE_URL once the hosting address is known. Without it, builds leave
// out canonical URLs and the sitemap.
const site = process.env.SITE_URL;

export default defineConfig({
  site,
  integrations: site ? [sitemap()] : [],
  vite: { plugins: [tailwindcss()] },
});
