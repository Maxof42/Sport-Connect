import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const MAP = {
  active: { label: "Inscriptions ouvertes", cls: "bg-emerald-100 text-emerald-800 border-emerald-200" },
  open: { label: "Inscriptions ouvertes", cls: "bg-emerald-100 text-emerald-800 border-emerald-200" },
  soon: { label: "Bientot", cls: "bg-amber-100 text-amber-800 border-amber-200" },
  closed: { label: "Inscriptions fermees", cls: "bg-neutral-200 text-neutral-700 border-neutral-300" },
  ghost: { label: "Page non activee", cls: "bg-neutral-100 text-neutral-500 border-neutral-200" },
  claimed: { label: "En moderation", cls: "bg-blue-100 text-blue-700 border-blue-200" },
};

export function StatusBadge({ club, className }) {
  let key = "closed";
  if (club.status === "ghost") key = "ghost";
  else if (club.status === "claimed") key = "claimed";
  else if (club.registration_open) key = "open";
  else if (club.season && club.season.toLowerCase().includes("suivante")) key = "soon";
  const m = MAP[key];
  return (
    <Badge data-testid="club-status-badge" variant="outline" className={cn("rounded-full border font-semibold", m.cls, className)}>
      {m.label}
    </Badge>
  );
}
