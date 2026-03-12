/**
 * Hooks React Query pour le Dashboard
 * Remplacent les hooks Supabase par des appels API FastAPI
 */

import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "@/lib/api";

export function useDashboardStats(month: string) {
  return useQuery({
    queryKey: ["dashboard", "stats", month],
    queryFn: () => dashboardApi.getStats(month),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCategoryBreakdown(month: string) {
  return useQuery({
    queryKey: ["dashboard", "breakdown", month],
    queryFn: () => dashboardApi.getBreakdown(month),
    staleTime: 5 * 60 * 1000,
  });
}

export function useMonthlyEvolution(months: number = 12) {
  return useQuery({
    queryKey: ["dashboard", "evolution", months],
    queryFn: () => dashboardApi.getEvolution(months),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Hook pour le comparatif par type de compte (à implémenter dans l'API)
export function useAccountTypeBreakdown(month: Date) {
  const monthStr = month.toISOString().slice(0, 7); // YYYY-MM
  return useQuery({
    queryKey: ["dashboard", "accounts", monthStr],
    queryFn: async () => {
      // Pour l'instant, retourner des données vides ou mock
      // TODO: Implémenter endpoint /api/dashboard/accounts dans FastAPI
      return [];
    },
    staleTime: 5 * 60 * 1000,
  });
}
