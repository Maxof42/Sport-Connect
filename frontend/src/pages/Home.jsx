import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { SearchBar } from "@/components/SearchBar";
import { sportIcon } from "@/lib/sportIcons";
import { Search, ClipboardCheck, CreditCard, ArrowRight } from "lucide-react";

const HERO_IMG =
  "https://images.unsplash.com/photo-1761941210086-d44de26a4efd?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzNTl8MHwxfHNlYXJjaHwxfHxydW5uaW5nJTIwdHJhY2slMjB0b3AlMjB2aWV3fGVufDB8fHx8MTc4MzkzMDQwN3ww&ixlib=rb-4.1.0&q=85";

const STEPS = [
  { icon: Search, title: "Cherchez", text: "Sport, age et code postal : trouvez les clubs pres de chez vous en 3 champs." },
  { icon: ClipboardCheck, title: "Comparez", text: "Fiches claires : niveau, creneaux, tarifs et disponibilite des inscriptions." },
  { icon: CreditCard, title: "Inscrivez-vous", text: "Inscription et paiement de la cotisation en ligne, confirmation par e-mail." },
];

export default function Home() {
  const [sports, setSports] = useState([]);
  const [stats, setStats] = useState({ clubs: 0, sports: 0 });

  useEffect(() => {
    api.get("/sports").then(({ data }) => {
      setSports(data.slice(0, 10));
      setStats((s) => ({ ...s, sports: data.length }));
    }).catch(() => {});
    api.get("/clubs", { params: { limit: 1 } }).then(({ data }) => {
      setStats((s) => ({ ...s, clubs: data.total }));
    }).catch(() => {});
  }, []);

  return (
    <div>
      {/* HERO */}
      <section className="relative overflow-hidden bg-[#0a0a0a] text-white">
        <div className="grain absolute inset-0 opacity-50" />
        <img src={HERO_IMG} alt="" className="absolute right-0 top-0 h-full w-1/2 object-cover opacity-25" />
        <div className="absolute inset-0 bg-gradient-to-r from-[#0a0a0a] via-[#0a0a0a]/95 to-transparent" />
        <div className="relative mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-28">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="max-w-2xl"
          >
            <p className="overline text-sport">Pilote Haute-Garonne · 31</p>
            <h1 className="mt-4 font-heading text-4xl font-black leading-[0.95] tracking-tight sm:text-5xl lg:text-6xl">
              Trouvez votre club de sport,<br />
              <span className="text-sport">inscrivez-vous</span> en ligne.
            </h1>
            <p className="mt-5 max-w-xl text-base text-white/70 sm:text-lg">
              Le lien direct entre les clubs de sport et les pratiquants du 31.
              Cherchez, comparez et reglez votre cotisation, comme prendre rendez-vous.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="mt-10 max-w-4xl"
          >
            <SearchBar variant="hero" />
          </motion.div>

          <div className="mt-8 flex flex-wrap gap-8 text-sm">
            <div>
              <span className="font-heading text-3xl font-extrabold text-sport">{stats.clubs}</span>
              <span className="ml-2 text-white/60">clubs referencies</span>
            </div>
            <div>
              <span className="font-heading text-3xl font-extrabold text-sport">{stats.sports}</span>
              <span className="ml-2 text-white/60">disciplines</span>
            </div>
          </div>
        </div>
      </section>

      {/* POPULAR SPORTS */}
      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8">
        <div className="flex items-end justify-between">
          <div>
            <p className="overline text-sport">Disciplines</p>
            <h2 className="mt-2 font-heading text-2xl font-bold tracking-tight sm:text-3xl">
              Explorez par sport
            </h2>
          </div>
          <Link to="/clubs" className="hidden items-center gap-1 text-sm font-semibold text-foreground hover:text-sport sm:flex">
            Tous les clubs <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {sports.map((s, i) => {
            const Icon = sportIcon(s.name);
            return (
              <motion.div
                key={s.name}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.3, delay: i * 0.03 }}
              >
                <Link
                  to={`/clubs?sport=${encodeURIComponent(s.name)}`}
                  data-testid="sport-chip"
                  className="group flex items-center gap-3 rounded-lg border border-border bg-card p-4 transition-all duration-200 hover:-translate-y-1 hover:border-sport"
                >
                  <span className="flex h-10 w-10 items-center justify-center rounded-md bg-[#0a0a0a] text-sport transition-colors group-hover:bg-sport group-hover:text-white">
                    <Icon className="h-5 w-5" strokeWidth={1.8} />
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate font-semibold leading-tight">{s.name}</span>
                    <span className="text-xs text-muted-foreground">{s.count} clubs</span>
                  </span>
                </Link>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="border-y border-border bg-secondary/50">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8">
          <h2 className="font-heading text-2xl font-bold tracking-tight sm:text-3xl">Comment ca marche</h2>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {STEPS.map((s, i) => (
              <div key={s.title} className="relative rounded-lg border border-border bg-card p-7">
                <span className="font-heading text-5xl font-black text-sport/20">0{i + 1}</span>
                <s.icon className="absolute right-6 top-6 h-6 w-6 text-sport" strokeWidth={1.8} />
                <h3 className="mt-4 font-heading text-xl font-bold">{s.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{s.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CLUB CTA */}
      <section className="mx-auto max-w-7xl px-5 py-20 sm:px-8">
        <div className="relative overflow-hidden rounded-2xl bg-[#0a0a0a] p-10 text-white sm:p-14">
          <div className="grain absolute inset-0 opacity-50" />
          <div className="relative max-w-2xl">
            <p className="overline text-sport">Vous gerez un club ?</p>
            <h2 className="mt-3 font-heading text-3xl font-black tracking-tight sm:text-4xl">
              Votre page existe deja. Revendiquez-la.
            </h2>
            <p className="mt-4 text-white/70">
              Comme sur Doctolib, votre club figure peut-etre deja dans notre annuaire du 31.
              Activez votre page, gerez vos inscriptions et vos paiements, sans commission.
            </p>
            <Link
              to="/register"
              data-testid="home-club-cta"
              className="mt-7 inline-flex items-center gap-2 rounded-full bg-sport px-6 py-3 font-bold text-white transition-transform hover:-translate-y-0.5"
            >
              Inscrire mon club <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
