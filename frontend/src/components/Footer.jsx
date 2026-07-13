import { Activity } from "lucide-react";

export function Footer() {
  return (
    <footer className="mt-24 border-t border-border bg-[#0a0a0a] text-white">
      <div className="mx-auto max-w-7xl px-5 py-14 sm:px-8">
        <div className="flex flex-col justify-between gap-8 md:flex-row">
          <div className="max-w-sm">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-sport" strokeWidth={2.5} />
              <span className="font-heading text-xl font-extrabold">
                Sport<span className="text-sport">Connect</span>
              </span>
            </div>
            <p className="mt-4 text-sm text-white/60">
              Le lien direct entre clubs de sport et pratiquants. Pilote Haute-Garonne (31),
              avant l'extension nationale.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-10 text-sm">
            <div>
              <p className="overline mb-3 text-white/40">Pratiquants</p>
              <ul className="space-y-2 text-white/70">
                <li>Trouver un club</li>
                <li>S'inscrire en ligne</li>
                <li>Paiement securise</li>
              </ul>
            </div>
            <div>
              <p className="overline mb-3 text-white/40">Clubs</p>
              <ul className="space-y-2 text-white/70">
                <li>Revendiquer sa page</li>
                <li>Gerer les inscriptions</li>
                <li>Abonnement par paliers</li>
              </ul>
            </div>
          </div>
        </div>
        <p className="mt-12 text-xs text-white/40">
          Donnees issues de l'open data Data-ES (equipements.sports.gouv.fr) · Licence Etalab 2.0.
        </p>
      </div>
    </footer>
  );
}
