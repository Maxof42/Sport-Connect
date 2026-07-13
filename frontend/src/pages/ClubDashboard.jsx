import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { api, apiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import { StatusBadge } from "@/components/StatusBadge";
import { LayoutDashboard, Search, Send, CreditCard, Building2 } from "lucide-react";

export default function ClubDashboard() {
  const [clubs, setClubs] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [club, setClub] = useState(null);
  const [enrollments, setEnrollments] = useState([]);
  const [info, setInfo] = useState({});
  const [reg, setReg] = useState({});
  const [announce, setAnnounce] = useState({ subject: "", message: "" });
  const [search, setSearch] = useState("");
  const [candidates, setCandidates] = useState([]);

  const loadMine = useCallback(async () => {
    const { data } = await api.get("/club/mine");
    setClubs(data);
    if (data.length && !selectedId) setSelectedId(data[0].id);
  }, [selectedId]);

  useEffect(() => { loadMine(); }, [loadMine]);

  const loadClub = useCallback(async () => {
    if (!selectedId) { setClub(null); return; }
    const { data } = await api.get(`/clubs/${selectedId}`);
    setClub(data);
    setInfo({
      description: data.description || "", level: data.level || "", fees: data.fees || "",
      phone: data.phone || "", email: data.email || "", website: data.website || "", schedule: data.schedule || "",
    });
    setReg({
      registration_open: !!data.registration_open, season: data.season || "Saison en cours",
      slots_total: data.slots_total || 0, slots_taken: data.slots_taken || 0, licensees: data.licensees || 0,
    });
    const en = await api.get(`/club/${selectedId}/enrollments`);
    setEnrollments(en.data);
  }, [selectedId]);

  useEffect(() => { loadClub(); }, [loadClub]);

  const saveInfo = async () => {
    try { await api.put(`/club/${selectedId}`, info); toast.success("Informations enregistrees"); loadClub(); }
    catch (e) { toast.error(apiError(e.response?.data?.detail)); }
  };

  const saveReg = async () => {
    try {
      await api.put(`/club/${selectedId}/registration`, {
        ...reg,
        slots_total: parseInt(reg.slots_total || 0, 10),
        slots_taken: parseInt(reg.slots_taken || 0, 10),
        licensees: parseInt(reg.licensees || 0, 10),
      });
      toast.success("Parametres d'inscription mis a jour"); loadClub();
    } catch (e) { toast.error(apiError(e.response?.data?.detail)); }
  };

  const subscribe = async () => {
    try { const { data } = await api.post(`/club/${selectedId}/subscribe`); toast.success(`Abonnement ${data.subscription.tier} confirme (demo)`); loadClub(); }
    catch (e) { toast.error(apiError(e.response?.data?.detail)); }
  };

  const sendAnnounce = async () => {
    try {
      const { data } = await api.post(`/club/${selectedId}/announce`, announce);
      toast.success(`Communication envoyee a ${data.recipients} adherent(s) (e-mail demo)`);
      setAnnounce({ subject: "", message: "" });
    } catch (e) { toast.error(apiError(e.response?.data?.detail)); }
  };

  const doSearch = async () => {
    const { data } = await api.get("/clubs", { params: { q: search, limit: 12 } });
    setCandidates(data.results);
  };

  const claim = async (id) => {
    try { await api.post(`/clubs/${id}/claim`); toast.success("Revendication envoyee (moderation admin)"); doSearch(); }
    catch (e) { toast.error(apiError(e.response?.data?.detail)); }
  };

  const tier = reg.licensees < 100 ? { t: "Petit club", p: 199 } : reg.licensees <= 500 ? { t: "Club moyen", p: 499 } : { t: "Grand club", p: 999 };

  return (
    <div className="mx-auto max-w-6xl px-5 py-10 sm:px-8">
      <div className="flex items-center gap-2">
        <LayoutDashboard className="h-6 w-6 text-sport" />
        <h1 className="font-heading text-2xl font-bold tracking-tight">Espace club</h1>
      </div>

      {/* CLAIM */}
      <div className="mt-8 rounded-xl border border-border bg-card p-6">
        <p className="overline text-sport">Revendiquer une page</p>
        <h2 className="mt-1 font-heading text-lg font-bold">Votre club existe deja dans l'annuaire ?</h2>
        <div className="mt-4 flex gap-2">
          <Input data-testid="claim-search" placeholder="Nom du club / equipement..." value={search}
            onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => e.key === "Enter" && doSearch()} />
          <Button data-testid="claim-search-btn" onClick={doSearch} className="rounded-full">
            <Search className="mr-2 h-4 w-4" /> Rechercher
          </Button>
        </div>
        {candidates.length > 0 && (
          <div className="mt-4 space-y-2">
            {candidates.map((c) => (
              <div key={c.id} className="flex items-center justify-between rounded-md border border-border p-3">
                <div>
                  <Link to={`/clubs/${c.id}`} className="font-semibold hover:text-sport">{c.name}</Link>
                  <p className="text-xs text-muted-foreground">{c.city} · {c.postal_code}</p>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge club={c} />
                  <Button size="sm" variant="outline" className="rounded-full" disabled={c.status === "active" || c.status === "claimed"}
                    onClick={() => claim(c.id)} data-testid="claim-candidate">
                    {c.status === "active" ? "Active" : c.status === "claimed" ? "En cours" : "Revendiquer"}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* OWNED CLUBS */}
      <h2 className="mt-12 font-heading text-xl font-bold">Mes clubs</h2>
      {clubs.length === 0 ? (
        <p className="mt-3 text-muted-foreground">
          Vous ne gerez aucun club actif. Revendiquez une page ci-dessus : elle sera activee apres validation par l'admin.
        </p>
      ) : (
        <>
          <div className="mt-4 flex flex-wrap gap-2">
            {clubs.map((c) => (
              <button key={c.id} data-testid="owned-club-tab" onClick={() => setSelectedId(c.id)}
                className={`rounded-full border px-4 py-2 text-sm font-semibold transition-colors ${
                  selectedId === c.id ? "border-sport bg-sport text-white" : "border-border bg-card hover:border-neutral-400"
                }`}>
                {c.name}
              </button>
            ))}
          </div>

          {club && (
            <div className="mt-6">
              <div className="mb-4 flex items-center gap-3">
                <Building2 className="h-5 w-5 text-sport" />
                <span className="font-heading text-lg font-bold">{club.name}</span>
                <StatusBadge club={club} />
              </div>

              <Tabs defaultValue="infos">
                <TabsList>
                  <TabsTrigger value="infos" data-testid="tab-infos">Infos</TabsTrigger>
                  <TabsTrigger value="reg" data-testid="tab-reg">Inscriptions</TabsTrigger>
                  <TabsTrigger value="enroll" data-testid="tab-enroll">Recues ({enrollments.length})</TabsTrigger>
                  <TabsTrigger value="sub" data-testid="tab-sub">Abonnement</TabsTrigger>
                  <TabsTrigger value="comm" data-testid="tab-comm">Communication</TabsTrigger>
                </TabsList>

                <TabsContent value="infos">
                  <div className="grid gap-4 rounded-lg border border-border bg-card p-6 sm:grid-cols-2">
                    <div className="sm:col-span-2">
                      <Label>Description</Label>
                      <Textarea data-testid="info-description" rows={3} value={info.description}
                        onChange={(e) => setInfo({ ...info, description: e.target.value })} className="mt-1" />
                    </div>
                    <div><Label>Niveau</Label><Input value={info.level} onChange={(e) => setInfo({ ...info, level: e.target.value })} className="mt-1" /></div>
                    <div><Label>Cotisation</Label><Input data-testid="info-fees" value={info.fees} onChange={(e) => setInfo({ ...info, fees: e.target.value })} className="mt-1" /></div>
                    <div><Label>Telephone</Label><Input value={info.phone} onChange={(e) => setInfo({ ...info, phone: e.target.value })} className="mt-1" /></div>
                    <div><Label>E-mail</Label><Input value={info.email} onChange={(e) => setInfo({ ...info, email: e.target.value })} className="mt-1" /></div>
                    <div><Label>Site web</Label><Input value={info.website} onChange={(e) => setInfo({ ...info, website: e.target.value })} className="mt-1" /></div>
                    <div><Label>Creneaux / horaires</Label><Input value={info.schedule} onChange={(e) => setInfo({ ...info, schedule: e.target.value })} className="mt-1" /></div>
                    <div className="sm:col-span-2">
                      <Button data-testid="save-info" onClick={saveInfo} className="rounded-full bg-sport font-bold text-white hover:bg-sport/90">Enregistrer</Button>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="reg">
                  <div className="grid gap-4 rounded-lg border border-border bg-card p-6 sm:grid-cols-2">
                    <div className="flex items-center justify-between rounded-md border border-border p-4 sm:col-span-2">
                      <div>
                        <p className="font-semibold">Inscriptions ouvertes</p>
                        <p className="text-xs text-muted-foreground">Autorise les participants a s'inscrire et payer en ligne.</p>
                      </div>
                      <Switch data-testid="reg-switch" checked={reg.registration_open}
                        onCheckedChange={(v) => setReg({ ...reg, registration_open: v })} />
                    </div>
                    <div><Label>Periode</Label><Input value={reg.season} onChange={(e) => setReg({ ...reg, season: e.target.value })} className="mt-1" /></div>
                    <div><Label>Nombre de licencies (declaration)</Label><Input data-testid="reg-licensees" type="number" value={reg.licensees} onChange={(e) => setReg({ ...reg, licensees: e.target.value })} className="mt-1" /></div>
                    <div><Label>Places totales</Label><Input type="number" value={reg.slots_total} onChange={(e) => setReg({ ...reg, slots_total: e.target.value })} className="mt-1" /></div>
                    <div><Label>Places prises</Label><Input type="number" value={reg.slots_taken} onChange={(e) => setReg({ ...reg, slots_taken: e.target.value })} className="mt-1" /></div>
                    <div className="sm:col-span-2">
                      <Button data-testid="save-reg" onClick={saveReg} className="rounded-full bg-sport font-bold text-white hover:bg-sport/90">Mettre a jour</Button>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="enroll">
                  <div className="rounded-lg border border-border bg-card p-2">
                    {enrollments.length === 0 ? (
                      <p className="p-6 text-center text-muted-foreground">Aucune inscription recue.</p>
                    ) : (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Participant</TableHead><TableHead>E-mail</TableHead>
                            <TableHead>Age</TableHead><TableHead>Paiement</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {enrollments.map((e) => (
                            <TableRow key={e.id} data-testid="club-enrollment-row">
                              <TableCell className="font-medium">{e.participant_name}</TableCell>
                              <TableCell>{e.participant_email}</TableCell>
                              <TableCell>{e.participant_age}</TableCell>
                              <TableCell><Badge className="rounded-full bg-emerald-100 text-emerald-800 hover:bg-emerald-100">Paye (demo)</Badge></TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="sub">
                  <div className="rounded-lg border border-border bg-card p-6">
                    <p className="overline text-muted-foreground">Palier calcule ({reg.licensees} licencies)</p>
                    <p className="mt-2 font-heading text-3xl font-extrabold">{tier.t}</p>
                    <p className="mt-1 text-muted-foreground">{tier.p} EUR / an · sans commission sur les inscriptions</p>
                    <div className="mt-4 flex items-center gap-3">
                      <Button data-testid="subscribe-btn" onClick={subscribe} className="rounded-full bg-sport font-bold text-white hover:bg-sport/90">
                        <CreditCard className="mr-2 h-4 w-4" /> Payer l'abonnement (demo)
                      </Button>
                      {club.subscription_active && <Badge className="rounded-full bg-emerald-100 text-emerald-800 hover:bg-emerald-100">Actif</Badge>}
                    </div>
                    <p className="mt-3 text-xs text-muted-foreground">Paliers : &lt;100 → 199€ · 100-500 → 499€ · &gt;500 → 999€</p>
                  </div>
                </TabsContent>

                <TabsContent value="comm">
                  <div className="space-y-4 rounded-lg border border-border bg-card p-6">
                    <p className="text-sm text-muted-foreground">
                      Envoyez un e-mail a tous les adherents inscrits (ex : annulation d'entrainement). Mode demo : e-mails simules.
                    </p>
                    <div><Label>Objet</Label><Input data-testid="announce-subject" value={announce.subject} onChange={(e) => setAnnounce({ ...announce, subject: e.target.value })} className="mt-1" /></div>
                    <div><Label>Message</Label><Textarea data-testid="announce-message" rows={4} value={announce.message} onChange={(e) => setAnnounce({ ...announce, message: e.target.value })} className="mt-1" /></div>
                    <Button data-testid="announce-send" onClick={sendAnnounce} disabled={!announce.subject || !announce.message}
                      className="rounded-full bg-sport font-bold text-white hover:bg-sport/90">
                      <Send className="mr-2 h-4 w-4" /> Envoyer a {enrollments.length} adherent(s)
                    </Button>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          )}
        </>
      )}
    </div>
  );
}
