import { useEffect, useState, useCallback } from "react";
import { api, apiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { ShieldCheck, Building2, Ticket, Clock, Users, Check, X } from "lucide-react";

function Stat({ icon: Icon, label, value }) {
  return (
    <div className="rounded-lg border border-border bg-card p-5">
      <Icon className="h-5 w-5 text-sport" />
      <p className="mt-3 font-heading text-3xl font-extrabold">{value}</p>
      <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
    </div>
  );
}

export default function AdminPanel() {
  const [stats, setStats] = useState(null);
  const [claims, setClaims] = useState([]);

  const load = useCallback(async () => {
    const [s, c] = await Promise.all([api.get("/admin/stats"), api.get("/admin/claims")]);
    setStats(s.data);
    setClaims(c.data);
  }, []);

  useEffect(() => { load(); }, [load]);

  const resolve = async (claimId, action) => {
    try {
      await api.post(`/admin/claims/${claimId}/${action}`);
      toast.success(action === "approve" ? "Page activee" : "Revendication refusee");
      load();
    } catch (err) {
      toast.error(apiError(err.response?.data?.detail));
    }
  };

  const pending = claims.filter((c) => c.status === "pending");

  return (
    <div className="mx-auto max-w-6xl px-5 py-10 sm:px-8">
      <div className="flex items-center gap-2">
        <ShieldCheck className="h-6 w-6 text-sport" />
        <h1 className="font-heading text-2xl font-bold tracking-tight">Administration</h1>
      </div>

      {stats && (
        <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
          <Stat icon={Building2} label="Clubs referencies" value={stats.clubs_total} />
          <Stat icon={Check} label="Clubs actives" value={stats.clubs_active} />
          <Stat icon={Ticket} label="Inscriptions" value={stats.enrollments} />
          <Stat icon={Clock} label="Revendications" value={stats.pending_claims} />
        </div>
      )}

      <h2 className="mt-12 font-heading text-xl font-bold">Revendications a moderer</h2>
      {pending.length === 0 ? (
        <p className="mt-4 text-muted-foreground">Aucune revendication en attente.</p>
      ) : (
        <div className="mt-4 space-y-3">
          {pending.map((c) => (
            <div key={c.id} data-testid="claim-row" className="flex flex-wrap items-center justify-between gap-4 rounded-lg border border-border bg-card p-5">
              <div>
                <p className="font-heading text-lg font-bold">{c.club_name}</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Demande par {c.user_name} · {c.user_email}
                </p>
              </div>
              <div className="flex gap-2">
                <Button data-testid="approve-claim" onClick={() => resolve(c.id, "approve")}
                  className="rounded-full bg-emerald-600 text-white hover:bg-emerald-700">
                  <Check className="mr-1.5 h-4 w-4" /> Approuver
                </Button>
                <Button data-testid="reject-claim" variant="outline" onClick={() => resolve(c.id, "reject")} className="rounded-full">
                  <X className="mr-1.5 h-4 w-4" /> Refuser
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <h2 className="mt-12 font-heading text-xl font-bold">Historique</h2>
      <div className="mt-4 space-y-2">
        {claims.filter((c) => c.status !== "pending").map((c) => (
          <div key={c.id} className="flex items-center justify-between rounded-lg border border-border bg-card px-5 py-3 text-sm">
            <span>{c.club_name} — {c.user_email}</span>
            <Badge variant="outline" className={c.status === "approved" ? "border-emerald-200 text-emerald-700" : "border-neutral-300 text-neutral-500"}>
              {c.status === "approved" ? "Approuvee" : "Refusee"}
            </Badge>
          </div>
        ))}
      </div>
    </div>
  );
}
