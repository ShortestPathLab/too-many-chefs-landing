export const SITE = {
  title: "Too Many Chefs",
  tagline: "The Open Kitchen Challenge",
  desc: "A cooking game inspired by Overcooked. Play using the keyboard or write a controller: a program that selects the chefs' actions.",
  lang: "en",
} as const;

export const NAV = [
  { href: "/", label: "Home" },
  { href: "/resources", label: "Resources" },
  { href: "/creators", label: "Creators" },
] as const;

export const LINKS = {
  github: "https://github.com/ShortestPathLab/too-many-chefs",
} as const;
