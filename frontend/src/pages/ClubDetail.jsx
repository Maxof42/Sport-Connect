import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { api, apiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { StatusBadge } from "@/components/StatusBadge";
import { sportIcon } from "@/lib/sportIcons";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import {
  MapPin, Trophy, Euro, Calendar, Users, ArrowLeft, CreditCard, CheckCircle2, ShieldPlus,
} from "lucide-react";

function InfoRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-start gap-3 py-3">
      <Icon className="mt-0.5 h-5 w-5 shrink-0 text-sport" strokeWidth={1.8} />
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{label}</p>
        <p className="mt-0.5 font-medium">{value || "Non renseigne"}</p>
      </div>
    </div>
  );
}

export default function ClubDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [club, setClub] = useState(null);
  const [open, setOpen] = useState(false);
  const [done, setDone] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({ participant_name: "", participant_email: "", participant_age: "", phone: "", notes: "" });

  const load = () => api.get(`/clubs/${id}`).then(({ data }) => setClub(data)).catch(() => setClub(false));
  useEffect(() => { load(); /* eslint-disable-next-line */ }, [id]);

  if (club === null) return <div className="flex min-h-[50vh] items-center justify-center text-muted-foreground">Chargement...</div>;
  if (club === false) return <div className="flex min-h-[50vh] items-center justify-center text-muted-foreground">Club introuvable.</div>;

  const Icon = sportIcon(club.sports?.[0] || "Multisports");

  const enroll = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post(`/clubs/${id}/enroll`, {
        ...form,
        participant_age: parseInt(form.participant_age || "0", 10),
      });
      setDone(true);
      toast.success("Inscription confirmee ! Un e-mail de confirmation a ete envoye.");
      load();
    } catch (err) {
      toast.error(apiError(err.response?.data?.detail));
    } finally {
      setSubmitting(false);
    }
  };

  const claim = async () => {
    try {
      await api.post(`/clubs/${id}/claim`);
      toast.success("Revendication envoyee. En attente de moderation.");
      load();
    } catch (err) {
      toast.error(apiError(err.response?.data?.detail));
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-5 py-8 sm:px-8">
      <Link to="/clubs" className="mb-6 inline-flex items-center gap-1.5 text-sm font-semibold text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Retour aux resultats
      </Link>

      {/* header */}
      <motion.div
        initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
        className="relative overflow-hidden rounded-xl bg-[#0a0a0a] p-8 text-white"
      >
        <div className="grain absolute inset-0 opacity-50" />
        <Icon className="absolute right-6 top-6 h-16 w-16 text-sport/40" strokeWidth={1} />
        <div className="relative">
          <StatusBadge club={club} className="mb-4" />
          <h1 className="font-heading text-3xl font-black tracking-tight sm:text-4xl" data-testid="club-detail-name">{club.name}</h1>
          <p className="mt-2 flex items-center gap-1.5 text-white/70">
            <MapPin className="h-4 w-4" /> {club.address ? `${club.address}, ` : ""}{club.postal_code} {club.city}
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {club.sports?.map((s) => (
              <Badge key={s} className="rounded-full bg-white/10 text-white hover:bg-white/20">{s}</Badge>
            ))}
          </div>
        </div>
      </motion.div>

      <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_320px]">
        <div>
          <h2 className="font-heading text-xl font-bold">A propos</h2>
          <p className="mt-3 text-muted-foreground">
            {club.description || "Ce club n'a pas encore complete sa presentation. Les informations proviennent de l'open data des equipements sportifs."}
          </p>
          {club.equip_types?.length > 0 && (
            <div className="mt-5">
              <p className="overline text-muted-foreground">Equipements</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {club.equip_types.map((t) => (
                  <Badge key={t} variant="secondary" className="rounded-full">{t}</Badge>
                ))}
              </div>
            </div>
          )}
          <Separator className="my-6" />
          <div className="grid grid-cols-1 sm:grid-cols-2">
            <InfoRow icon={Trophy} label="Niveau" value={club.level} />
            <InfoRow icon={Euro} label="Cotisation" value={club.fees} />
            <InfoRow icon={Calendar} label="Periode" value={club.season} />
            <InfoRow icon={Users} label="Age" value={`${club.age_min} - ${club.age_max} ans`} />
          </div>
        </div>

        {/* sidebar action */}
        <div className="lg:sticky lg:top-20 lg:self-start">
          <div className="rounded-xl border border-border bg-card p-6">
            <StatusBadge club={club} />
            {club.registration_open ? (
              <>
                <div className="mt-4">
                  <p className="font-heading text-2xl font-extrabold">{club.fees || "Cotisation a venir"}</p>
                  {club.slots_total > 0 && (
                    <p className="mt-1 text-sm text-muted-foreground">
                      {Math.max(0, club.slots_total - club.slots_taken)} place(s) disponible(s)
                    </p>
                  )}
                </div>
                <Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) setDone(false); }}>
                  <DialogTrigger asChild>
                    <Button data-testid="open-enroll" className="mt-5 w-full rounded-full bg-sport font-bold text-white hover:bg-sport/90">
                      S'inscrire en ligne
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-md">
                    {done ? (
                      <div className="py-6 text-center">
                        <CheckCircle2 className="mx-auto h-14 w-14 text-emerald-500" />
                        <h3 className="mt-4 font-heading text-xl font-bold">Inscription confirmee</h3>
                        <p className="mt-2 text-sm text-muted-foreground">
                          Paiement de la cotisation valide (simule). Un e-mail de confirmation a ete envoye a {form.participant_email}.
                        </p>
                        <Button className="mt-6 rounded-full" onClick={() => setOpen(false)} data-testid="close-enroll">Fermer</Button>
                      </div>
                    ) : (
                      <form onSubmit={enroll}>
                        <DialogHeader>
                          <DialogTitle className="font-heading">Inscription · {club.name}</DialogTitle>
                        </DialogHeader>
                        <div className="mt-4 space-y-3">
                          <div>
                            <Label>Nom complet</Label>
                            <Input data-testid="enroll-name" required value={form.participant_name}
                              onChange={(e) => setForm({ ...form, participant_name: e.target.value })} className="mt-1" />
                          </div>
                          <div>
                            <Label>E-mail</Label>
                            <Input data-testid="enroll-email" type="email" required value={form.participant_email}
                              onChange={(e) => setForm({ ...form, participant_email: e.target.value })} className="mt-1" />
                          </div>
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <Label>Age</Label>
                              <Input data-testid="enroll-age" type="number" required min={1} max={99} value={form.participant_age}
                                onChange={(e) => setForm({ ...form, participant_age: e.target.value })} className="mt-1" />
                            </div>
                            <div>
                              <Label>Telephone</Label>
                              <Input data-testid="enroll-phone" value={form.phone}
                                onChange={(e) => setForm({ ...form, phone: e.target.value })} className="mt-1" />
                            </div>
                          </div>
                          <div>
                            <Label>Message (optionnel)</Label>
                            <Textarea data-testid="enroll-notes" value={form.notes}
                              onChange={(e) => setForm({ ...form, notes: e.target.value })} className="mt-1" rows={2} />
                          </div>
                          <div className="flex items-center gap-2 rounded-md bg-secondary p-3 text-xs text-muted-foreground">
                            <CreditCard className="h-4 w-4 shrink-0" />
                            Paiement securise Stripe · <strong>mode demo (simule)</strong>. Aucune carte requise.
                          </div>
                        </div>
                        <DialogFooter className="mt-4">
                          <Button data-testid="submit-enroll" type="submit" disabled={submitting}
                            className="w-full rounded-full bg-sport font-bold text-white hover:bg-sport/90">
                            {submitting ? "Traitement..." : `Payer ${club.fees || "la cotisation"} et s'inscrire`}
                          </Button>
                        </DialogFooter>
                      </form>
                    )}
                  </DialogContent>
                </Dialog>
              </>
            ) : (
              <p className="mt-4 text-sm text-muted-foreground">
                Les inscriptions ne sont pas ouvertes actuellement pour ce club.
              </p>
            )}

            {user?.role === "club" && club.status !== "active" && (
              <Button onClick={claim} variant="outline" data-testid="claim-club"
                className="mt-3 w-full rounded-full" disabled={club.status === "claimed"}>
                <ShieldPlus className="mr-2 h-4 w-4" />
                {club.status === "claimed" ? "Revendication en cours" : "Revendiquer cette page"}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
