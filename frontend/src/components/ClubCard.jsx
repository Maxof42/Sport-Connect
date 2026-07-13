import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { MapPin, ArrowUpRight } from "lucide-react";
import { StatusBadge } from "@/components/StatusBadge";
import { sportIcon } from "@/lib/sportIcons";
import { Badge } from "@/components/ui/badge";

export function ClubCard({ club, index = 0, onHover, active }) {
  const primary = club.sports?.[0] || "Multisports";
  const Icon = sportIcon(primary);
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: Math.min(index * 0.04, 0.4) }}
      onMouseEnter={() => onHover?.(club.id)}
      data-testid="club-card"
    >
      <Link
        to={`/clubs/${club.id}`}
        className={`group block overflow-hidden rounded-lg border bg-card transition-transform duration-200 hover:-translate-y-1 ${
          active ? "border-sport ring-1 ring-sport" : "border-border hover:border-neutral-400"
        }`}
      >
        <div className="relative flex h-28 items-center justify-between bg-[#0a0a0a] px-5">
          <div className="grain absolute inset-0 opacity-60" />
          <Icon className="relative h-10 w-10 text-sport" strokeWidth={1.5} />
          <span className="relative overline text-white/60">{primary}</span>
        </div>
        <div className="space-y-3 p-5">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-heading text-lg font-bold leading-tight text-foreground line-clamp-2">
              {club.name}
            </h3>
            <ArrowUpRight className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-sport" />
          </div>
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <MapPin className="h-4 w-4 shrink-0" />
            <span className="truncate">{club.city} · {club.postal_code}</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {club.sports?.slice(0, 3).map((s) => (
              <Badge key={s} variant="secondary" className="rounded-full text-xs font-medium">{s}</Badge>
            ))}
          </div>
          <div className="flex items-center justify-between pt-1">
            <StatusBadge club={club} />
            <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{club.level}</span>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
