import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider } from "@/context/AuthContext";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { ProtectedRoute } from "@/components/ProtectedRoute";

import Home from "@/pages/Home";
import Results from "@/pages/Results";
import ClubDetail from "@/pages/ClubDetail";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import ClubDashboard from "@/pages/ClubDashboard";
import AdminPanel from "@/pages/AdminPanel";
import MyEnrollments from "@/pages/MyEnrollments";

function Shell({ children }) {
  return (
    <div className="App flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Shell>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/clubs" element={<Results />} />
            <Route path="/clubs/:id" element={<ClubDetail />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/mes-inscriptions"
              element={
                <ProtectedRoute roles={["participant", "club", "admin"]}>
                  <MyEnrollments />
                </ProtectedRoute>
              }
            />
            <Route
              path="/espace-club"
              element={
                <ProtectedRoute roles={["club", "admin"]}>
                  <ClubDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute roles={["admin"]}>
                  <AdminPanel />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Shell>
        <Toaster position="top-center" richColors />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
