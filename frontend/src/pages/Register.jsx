import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { apiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Activity, User, Building2 } from "lucide-react";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [role, setRole] = useState("participant");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      await register({ ...form, role });
      navigate(role === "club" ? "/espace-club" : "/");
    } catch (err) {
      setError(apiError(err.response?.data?.detail) || "Inscription impossible");
    } finally {
      setLoading(false);
    }
  };

  const roles = [
    { key: "participant", label: "Pratiquant / parent", icon: User },
    { key: "club", label: "Club de sport", icon: Building2 },
  ];

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-5 py-12">
      <div className="mb-8 flex items-center gap-2">
        <Activity className="h-6 w-6 text-sport" strokeWidth={2.5} />
        <span className="font-heading text-2xl font-extrabold">Creer un compte</span>
      </div>
      <form onSubmit={submit} className="space-y-4 rounded-xl border border-border bg-card p-6">
        <div className="grid grid-cols-2 gap-3">
          {roles.map((r) => (
            <button
              key={r.key} type="button" data-testid={`role-${r.key}`}
              onClick={() => setRole(r.key)}
              className={`flex flex-col items-center gap-2 rounded-lg border p-4 text-sm font-semibold transition-colors ${
                role === r.key ? "border-sport bg-sport/5 text-foreground" : "border-border text-muted-foreground hover:border-neutral-400"
              }`}
            >
              <r.icon className="h-5 w-5" /> {r.label}
            </button>
          ))}
        </div>
        <div>
          <Label>{role === "club" ? "Nom du club / responsable" : "Nom complet"}</Label>
          <Input data-testid="register-name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="mt-1" />
        </div>
        <div>
          <Label>E-mail</Label>
          <Input data-testid="register-email" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="mt-1" />
        </div>
        <div>
          <Label>Mot de passe (6 caracteres min.)</Label>
          <Input data-testid="register-password" type="password" required minLength={6} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="mt-1" />
        </div>
        {error && <p data-testid="register-error" className="text-sm font-medium text-destructive">{error}</p>}
        <Button data-testid="register-submit" type="submit" disabled={loading} className="w-full rounded-full bg-sport font-bold text-white hover:bg-sport/90">
          {loading ? "Creation..." : "Creer mon compte"}
        </Button>
        <p className="text-center text-sm text-muted-foreground">
          Deja inscrit ? <Link to="/login" className="font-semibold text-foreground hover:text-sport">Se connecter</Link>
        </p>
      </form>
    </div>
  );
}
