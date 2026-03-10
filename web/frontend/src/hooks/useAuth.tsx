/**
 * @file useAuth.tsx
 * @description Hook d'authentification - VERSION ADAPTÉE POUR FASTAPI
 * 
 * ⚠️  À ADAPTER : Remplacer l'appel à Supabase par des appels à l'API FastAPI
 * 
 * Cette version utilise un mock local pour permettre le développement frontend
 * indépendamment de l'API. À remplacer par des appels fetch vers /api/auth/*
 */

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";

// TODO: Définir ces types dans un fichier types/auth.ts
interface User {
  id: string;
  email: string;
  displayName?: string;
}

interface Session {
  user: User;
  token: string;
}

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signUp: (email: string, password: string, displayName?: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

// ============================================
// MOCK LOCAL - À REMPLACER PAR API FASTAPI
// ============================================
const MOCK_USER: User = {
  id: "mock-user-001",
  email: "demo@financeperso.local",
  displayName: "Utilisateur Demo",
};

const MOCK_SESSION: Session = {
  user: MOCK_USER,
  token: "mock-jwt-token",
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const queryClient = useQueryClient();

  useEffect(() => {
    // TODO: Remplacer par : GET /api/auth/me ou vérification du token stocké
    // Simulation d'une vérification de session
    const checkSession = async () => {
      try {
        // Mock : auto-login pour le développement
        // En prod : vérifier le token JWT stocké
        const storedToken = localStorage.getItem("fp_token");
        if (storedToken) {
          setSession(MOCK_SESSION);
          setUser(MOCK_USER);
        }
      } catch (error) {
        console.error("Session check failed:", error);
      } finally {
        setLoading(false);
      }
    };

    checkSession();
  }, []);

  const signUp = async (email: string, password: string, displayName?: string) => {
    // TODO: Remplacer par : POST /api/auth/register
    console.log("[MOCK] Sign up:", { email, password, displayName });
    
    // Simulation
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const newUser: User = {
      id: `user-${Date.now()}`,
      email,
      displayName,
    };
    
    const newSession: Session = {
      user: newUser,
      token: `token-${Date.now()}`,
    };
    
    localStorage.setItem("fp_token", newSession.token);
    setSession(newSession);
    setUser(newUser);
  };

  const signIn = async (email: string, password: string) => {
    // TODO: Remplacer par : POST /api/auth/login
    console.log("[MOCK] Sign in:", { email, password });
    
    // Simulation
    await new Promise(resolve => setTimeout(resolve, 500));
    
    localStorage.setItem("fp_token", MOCK_SESSION.token);
    setSession(MOCK_SESSION);
    setUser(MOCK_USER);
  };

  const signOut = async () => {
    // TODO: Remplacer par : POST /api/auth/logout
    console.log("[MOCK] Sign out");
    
    localStorage.removeItem("fp_token");
    setSession(null);
    setUser(null);
    queryClient.clear();
  };

  return (
    <AuthContext.Provider value={{ user, session, loading, signUp, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}
