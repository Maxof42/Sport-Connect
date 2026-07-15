import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "@/lib/api";
import { SearchBar } from "@/components/SearchBar";
import { ClubCard } from "@/components/ClubCard";
import { MapView } from "@/components/MapView";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { SlidersHorizontal, MapPin } from "lucide-react";

export default function Results() {
  const [params] = useSearchParams();
  const [data, setData] = useState({ results: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [activeId, setActiveId] = useState(null);
  const [showMap, setShowMap] = useState(true);

  const sport = params.get("sport") || "";
  const cp = params.get("postal_code") || "";
  const age = params.get("age") || "";
  const nameQuery = params.get("q") || "";

  const fetchClubs = useCallback(async () => {
    setLoading(true);
    try {
      const q = { page, limit: 24 };
      if (sport) q.sport = sport;
      if (cp) q.postal_code = cp;
      if (age) q.age = age;
      if (nameQuery) q.q = nameQuery;
      const { data } = await api.get("/clubs", { params: q });
      setData(data);
    } finally {
      setLoading(false);
    }
  }, [sport, cp, age, nameQuery, page]);

  useEffect(() => { setPage(1); }, [sport, cp, age, nameQuery]);
  useEffect(() => { fetchClubs(); }, [fetchClubs]);

  const totalPages = Math.ceil(data.total / 24) || 1;
  const clubsWithLoc = data.results.filter((c) => c.location);

  return (
    <div>
      <div className="border-b border-border bg-secondary/40">
        <div className="mx-auto max-w-7xl px-5 py-6 sm:px-8">
          <SearchBar variant="results" initial={{ sport, postal_code: cp, age, q: nameQuery }} />
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-5 py-8 sm:px-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="font-heading text-2xl font-bold tracking-tight" data-testid="results-title">
              {loading ? "Recherche..." : `${data.total} club${data.total > 1 ? "s" : ""} trouve${data.total > 1 ? "s" : ""}`}
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {nameQuery ? `« ${nameQuery} » · ` : ""}{sport ? `${sport} · ` : ""}{cp ? `${cp} · ` : ""}Haute-Garonne (31)
            </p>
          </div>
          <Button
            variant="outline"
            className="rounded-full lg:hidden"
            onClick={() => setShowMap((v) => !v)}
            data-testid="toggle-map"
          >
            <MapPin className="mr-2 h-4 w-4" /> {showMap ? "Masquer la carte" : "Carte"}
          </Button>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_420px]">
          <div>
            {loading ? (
              <div className="grid gap-4 sm:grid-cols-2">
                {Array.from({ length: 6 }).map((_, i) => (
                  <Skeleton key={i} className="h-56 rounded-lg" />
                ))}
              </div>
            ) : data.results.length === 0 ? (
              <div className="rounded-lg border border-dashed border-border p-16 text-center">
                <SlidersHorizontal className="mx-auto h-8 w-8 text-muted-foreground" />
                <p className="mt-4 font-heading text-lg font-bold">Aucun club ne correspond</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Elargissez votre recherche (autre sport ou code postal du 31).
                </p>
              </div>
            ) : (
              <>
                <div className="grid gap-4 sm:grid-cols-2">
                  {data.results.map((c, i) => (
                    <ClubCard key={c.id} club={c} index={i} onHover={setActiveId} active={c.id === activeId} />
                  ))}
                </div>
                {totalPages > 1 && (
                  <div className="mt-8 flex items-center justify-center gap-3">
                    <Button
                      variant="outline" className="rounded-full" disabled={page <= 1}
                      onClick={() => setPage((p) => p - 1)} data-testid="prev-page"
                    >
                      Precedent
                    </Button>
                    <span className="text-sm text-muted-foreground">Page {page} / {totalPages}</span>
                    <Button
                      variant="outline" className="rounded-full" disabled={page >= totalPages}
                      onClick={() => setPage((p) => p + 1)} data-testid="next-page"
                    >
                      Suivant
                    </Button>
                  </div>
                )}
              </>
            )}
          </div>

          <div className={`${showMap ? "block" : "hidden"} lg:block`}>
            <div className="sticky top-20">
              <MapView clubs={clubsWithLoc} activeId={activeId} onSelect={setActiveId} />
              <p className="mt-2 text-center text-xs text-muted-foreground">
                Cliquez un point pour le reperer · double-clic pour ouvrir la fiche
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
