export const SITE = {
  title: "Too Many Chefs!",
  tagline: "The Last Cooking Simulator You Need",
  desc: "A configurable cooking simulator for AI research and education. Play a kitchen yourself, or write a controller that chooses the chefs' actions.",
  lang: "en",
  lab: { name: "ShortestPathLab", href: "https://pathfinding.ai/" },
} as const;

// Resources and Creators point at sections of the home page for now. Switch
// them to "/resources" and "/creators" once those pages are finished.
export const NAV = [
  { href: "/", label: "Home" },
  { href: "/#resources", label: "Resources" },
  { href: "/#creators", label: "Creators" },
] as const;

export type Resource = {
  id: string;
  title: string;
  kind: string;
  desc: string;
  // Leave out until the resource is published. The tile then reads "Coming soon".
  href?: string;
};

export const RESOURCES: Resource[] = [
  {
    id: "code",
    title: "Source code",
    kind: "GitHub",
    desc: "The simulator, starter controller, levels and docs.",
    href: "https://github.com/ShortestPathLab/too-many-chefs",
  },
  {
    id: "video",
    title: "Demo video",
    kind: "YouTube",
    desc: "A short tour of the kitchens, modes and tools.",
  },
  {
    id: "guide",
    title: "Kitchen Guide",
    kind: "PDF",
    desc: "How the simulator works and what each level asks for.",
    href: "https://github.com/ShortestPathLab/too-many-chefs-kitchen-guide/releases/latest",
  },
  {
    id: "paper",
    title: "Demo paper",
    kind: "AAAI-27",
    desc: "The simulator's design and its integrations.",
  },
];

export const resource = (id: string) => RESOURCES.find(r => r.id === id)!;

export const CREATORS = [
  { name: "Kevin Zheng", affiliation: "Monash University" },
  { name: "Daniel Harabor", affiliation: "Monash University" },
] as const;

export const MODES = [
  {
    name: "Play",
    desc: "Walk a chef around with the keyboard and deliver the orders yourself.",
  },
  {
    name: "Agent",
    desc: "Write a controller. PDDL, Gymnasium and PettingZoo examples are included.",
  },
  {
    name: "Replay",
    desc: "Step back and forward through a recording to see what each chef did.",
  },
] as const;
