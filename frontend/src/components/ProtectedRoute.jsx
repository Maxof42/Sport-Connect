import { useAuth } from "@/context/AuthContext";
import { Navigate, useLocation } from "react-router-dom";

export function ProtectedRoute({ children, roles }) {
  const { user, ready } = useAuth();
  const location = useLocation();

  if (!ready || user === null) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center text-muted-foreground">
        Chargement...
      </div>
    );
  }
  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }
  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }
  return children;
}
