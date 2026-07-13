import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Activity, LogOut, LayoutDashboard, ShieldCheck, Ticket } from "lucide-react";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const doLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/85 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 sm:px-8">
        <Link to="/" data-testid="nav-logo" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-md bg-[#0a0a0a]">
            <Activity className="h-5 w-5 text-sport" strokeWidth={2.5} />
          </span>
          <span className="font-heading text-xl font-extrabold tracking-tight">
            Sport<span className="text-sport">Connect</span>
          </span>
        </Link>

        <nav className="flex items-center gap-2 sm:gap-3">
          <Link to="/clubs" data-testid="nav-clubs" className="hidden px-3 text-sm font-semibold text-foreground/80 hover:text-foreground sm:block">
            Trouver un club
          </Link>

          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button data-testid="nav-user-menu" variant="outline" className="rounded-full">
                  {user.name?.split(" ")[0] || "Compte"}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-52">
                {user.role === "participant" && (
                  <DropdownMenuItem onClick={() => navigate("/mes-inscriptions")} data-testid="nav-my-enrollments">
                    <Ticket className="mr-2 h-4 w-4" /> Mes inscriptions
                  </DropdownMenuItem>
                )}
                {user.role === "club" && (
                  <DropdownMenuItem onClick={() => navigate("/espace-club")} data-testid="nav-club-space">
                    <LayoutDashboard className="mr-2 h-4 w-4" /> Espace club
                  </DropdownMenuItem>
                )}
                {user.role === "admin" && (
                  <DropdownMenuItem onClick={() => navigate("/admin")} data-testid="nav-admin">
                    <ShieldCheck className="mr-2 h-4 w-4" /> Administration
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={doLogout} data-testid="nav-logout">
                  <LogOut className="mr-2 h-4 w-4" /> Deconnexion
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <>
              <Button data-testid="nav-login" variant="ghost" onClick={() => navigate("/login")} className="rounded-full">
                Connexion
              </Button>
              <Button
                data-testid="nav-register"
                onClick={() => navigate("/register")}
                className="rounded-full bg-[#0a0a0a] text-white hover:bg-neutral-800"
              >
                Inscrire mon club
              </Button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
