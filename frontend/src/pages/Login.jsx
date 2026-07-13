import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { apiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Activity } from "lucide-react";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      const u = await login(email, password);
      const dest = u.role === "admin" ? "/admin" : u.role === "club" ? "/espace-club" : (location.state?.from || "/");
      navigate(dest);
    } catch (err) {
      setError(apiError(err.response?.data?.detail) || "Connexion impossible");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-5 py-12">
      <div className="mb-8 flex items-center gap-2">
        <Activity className="h-6 w-6 text-sport" strokeWidth={2.5} />
        <span className="font-heading text-2xl font-extrabold">Connexion</span>
      </div>
      <form onSubmit={submit} className="space-y-4 rounded-xl border border-border bg-card p-6">
        <div>
          <Label>E-mail</Label>
          <Input data-testid="login-email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="mt-1" />
        </div>
        <div>
          <Label>Mot de passe</Label>
          <Input data-testid="login-password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="mt-1" />
        </div>
        {error && <p data-testid="login-error" className="text-sm font-medium text-destructive">{error}</p>}
        <Button data-testid="login-submit" type="submit" disabled={loading} className="w-full rounded-full bg-sport font-bold text-white hover:bg-sport/90">
          {loading ? "Connexion..." : "Se connecter"}
        </Button>
        <p className="text-center text-sm text-muted-foreground">
          Pas de compte ? <Link to="/register" className="font-semibold text-foreground hover:text-sport">Creer un compte</Link>
        </p>
      </form>
    </div>
  );
}
