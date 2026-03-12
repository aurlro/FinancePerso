/**
 * @file useAuth.tsx
 * @description Hook d'authentification - Utilise l'API FastAPI
 * 
 * Endpoints utilisés:
 * - POST /api/auth/register
 * - POST /api/auth/login
 * - GET /api/auth/me
 * - POST /api/auth/refresh
 * - POST /api/auth/logout
 */

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { authApi, setAuthToken, clearAuthToken } from "@/lib/api";

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

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const queryClient = useQueryClient();

  // Check for existing session on mount
  useEffect(() => {
    const checkSession = async () => {
      try {
        // Try to get current user - this validates the stored token
        const userData = await authApi.me();
        
        // If successful, restore the session
        const token = localStorage.getItem("auth_token");
        if (token) {
          setSession({
            user: {
              id: userData.id.toString(),
              email: userData.email,
              displayName: userData.name,
            },
            token,
          });
          setUser({
            id: userData.id.toString(),
            email: userData.email,
            displayName: userData.name,
          });
        }
      } catch (error) {
        // Token is invalid or expired - clear it
        console.log("Session invalid, clearing tokens");
        clearAuthToken();
        localStorage.removeItem("refresh_token");
      } finally {
        setLoading(false);
      }
    };

    checkSession();
  }, []);

  const signUp = async (email: string, password: string, displayName?: string) => {
    try {
      // Register new user
      const newUser = await authApi.register({
        email,
        password,
        name: displayName || email.split("@")[0],
      });

      // Auto-login after registration
      const tokens = await authApi.login({ email, password });

      // Set session
      setSession({
        user: {
          id: tokens.user.id.toString(),
          email: tokens.user.email,
          displayName: tokens.user.name,
        },
        token: tokens.access_token,
      });
      setUser({
        id: tokens.user.id.toString(),
        email: tokens.user.email,
        displayName: tokens.user.name,
      });
    } catch (error) {
      console.error("Sign up failed:", error);
      throw error;
    }
  };

  const signIn = async (email: string, password: string) => {
    try {
      const tokens = await authApi.login({ email, password });

      setSession({
        user: {
          id: tokens.user.id.toString(),
          email: tokens.user.email,
          displayName: tokens.user.name,
        },
        token: tokens.access_token,
      });
      setUser({
        id: tokens.user.id.toString(),
        email: tokens.user.email,
        displayName: tokens.user.name,
      });
    } catch (error) {
      console.error("Sign in failed:", error);
      throw error;
    }
  };

  const signOut = async () => {
    try {
      // Call logout endpoint (optional - token will be invalidated on client side anyway)
      // await authApi.logout();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      // Clear tokens and state
      authApi.logout();
      setSession(null);
      setUser(null);
      queryClient.clear();
    }
  };

  return (
    <AuthContext.Provider value={{ user, session, loading, signUp, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}
