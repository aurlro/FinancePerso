/**
 * Hooks React Query pour Analytics Avancés (PR #9)
 * Prédictions, tendances, détection d'anomalies
 */

import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";

// Hook pour détecter les anomalies
export function useAnomalies(threshold: number = 2.0) {
  return useQuery({
    queryKey: ["analytics", "anomalies", threshold],
    queryFn: () => analyticsApi.getAnomalies(threshold),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Hook pour les prédictions de cashflow
export function useCashflowPredictions(monthsAhead: number = 3) {
  return useQuery({
    queryKey: ["analytics", "predictions", "cashflow", monthsAhead],
    queryFn: () => analyticsApi.getCashflowPredictions(monthsAhead),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Hook pour les transactions récurrentes
export function useRecurringTransactions() {
  return useQuery({
    queryKey: ["analytics", "recurring"],
    queryFn: () => analyticsApi.getRecurringTransactions(),
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

// Hook pour les tendances par catégorie
export function useCategoryTrends(months: number = 6, category?: string) {
  return useQuery({
    queryKey: ["analytics", "trends", "categories", months, category],
    queryFn: () => analyticsApi.getCategoryTrends(months, category),
    staleTime: 10 * 60 * 1000,
    enabled: months >= 3,
  });
}

// Hook pour l'analyse de saisonnalité
export function useSeasonality(category?: string) {
  return useQuery({
    queryKey: ["analytics", "seasonality", category],
    queryFn: () => analyticsApi.getSeasonality(category),
    staleTime: 60 * 60 * 1000, // 1 hour
  });
}

// Hook pour les insights de dépenses
export function useSpendingInsights() {
  return useQuery({
    queryKey: ["analytics", "insights"],
    queryFn: () => analyticsApi.getSpendingInsights(),
    staleTime: 5 * 60 * 1000,
  });
}

// Hook pour la comparaison de périodes
export function usePeriodComparison(period: "month" | "quarter" | "year") {
  return useQuery({
    queryKey: ["analytics", "comparison", period],
    queryFn: () => analyticsApi.getPeriodComparison(period),
    staleTime: 10 * 60 * 1000,
  });
}
