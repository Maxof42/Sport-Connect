import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Ticket, ArrowRight } from "lucide-react";

export default function MyEnrollments() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/my/enrollments").then(({ data }) => setRows(data)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-4xl px-5 py-10 sm:px-8">
      <div className="flex items-center gap-2">
        <Ticket className="h-6 w-6 text-sport" />
        <h1 className="font-heading text-2xl font-bold tracking-tight">Mes inscriptions</h1>
      </div>

      {loading ? (
        <p className="mt-8 text-muted-foreground">Chargement...</p>
      ) : rows.length === 0 ? (
        <div className="mt-8 rounded-lg border border-dashed border-border p-14 text-center">
          <p className="font-heading text-lg font-bold">Aucune inscription pour le moment</p>
          <Link to="/clubs" className="mt-4 inline-flex items-center gap-1.5 font-semibold text-sport">
            Trouver un club <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      ) : (
        <div className="mt-8 space-y-3">
          {rows.map((r) => (
            <div key={r.id} data-testid="enrollment-row" className="flex items-center justify-between rounded-lg border border-border bg-card p-5">
              <div>
                <Link to={`/clubs/${r.club_id}`} className="font-heading text-lg font-bold hover:text-sport">{r.club_name}</Link>
                <p className="mt-1 text-sm text-muted-foreground">
                  {r.participant_name} · {r.season} · {r.fees || "cotisation"}
                </p>
              </div>
              <Badge className="rounded-full bg-emerald-100 text-emerald-800 hover:bg-emerald-100">
                {r.payment_status === "paid" ? "Paye (demo)" : r.payment_status}
              </Badge>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
