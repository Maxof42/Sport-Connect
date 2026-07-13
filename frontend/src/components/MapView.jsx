import { useNavigate } from "react-router-dom";
import { MapPin } from "lucide-react";

// Bounding box approx Haute-Garonne (31)
const LAT_MAX = 43.95, LAT_MIN = 42.65, LON_MIN = 0.4, LON_MAX = 2.1;

function project(loc) {
  if (!loc) return null;
  const x = ((loc.lon - LON_MIN) / (LON_MAX - LON_MIN)) * 100;
  const y = ((LAT_MAX - loc.lat) / (LAT_MAX - LAT_MIN)) * 100;
  return { x: Math.max(3, Math.min(97, x)), y: Math.max(4, Math.min(96, y)) };
}

export function MapView({ clubs, activeId, onSelect }) {
  const navigate = useNavigate();
  return (
    <div
      data-testid="clubs-map"
      className="relative h-full min-h-[420px] w-full overflow-hidden rounded-lg border border-border bg-[#0e1116]"
    >
      <div className="grain absolute inset-0 opacity-40" />
      {/* faux grid */}
      <div
        className="absolute inset-0 opacity-[0.15]"
        style={{
          backgroundImage:
            "linear-gradient(#2a3340 1px, transparent 1px), linear-gradient(90deg, #2a3340 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />
      <div className="absolute left-4 top-4 z-10 rounded-md bg-black/50 px-3 py-1.5 backdrop-blur">
        <p className="overline text-white/70">Haute-Garonne · 31</p>
      </div>
      <div className="absolute bottom-4 right-4 z-10 rounded-md bg-black/50 px-3 py-1.5 text-xs text-white/70 backdrop-blur">
        {clubs.length} club{clubs.length > 1 ? "s" : ""} localise{clubs.length > 1 ? "s" : ""}
      </div>
      {clubs.map((c) => {
        const p = project(c.location);
        if (!p) return null;
        const isActive = c.id === activeId;
        return (
          <button
            key={c.id}
            data-testid="map-marker"
            onClick={() => onSelect?.(c.id)}
            onDoubleClick={() => navigate(`/clubs/${c.id}`)}
            title={c.name}
            className="absolute z-20 -translate-x-1/2 -translate-y-1/2 transition-transform duration-150 hover:scale-125"
            style={{ left: `${p.x}%`, top: `${p.y}%` }}
          >
            <MapPin
              className={isActive ? "h-7 w-7 text-sport drop-shadow" : "h-5 w-5 text-white/80"}
              fill={isActive ? "currentColor" : "none"}
              strokeWidth={2}
            />
          </button>
        );
      })}
    </div>
  );
}
