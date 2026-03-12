/**
 * Hooks React Query pour les Budgets
 * Remplacent les hooks Supabase par des appels API FastAPI
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { budgetsApi, type Budget } from "@/lib/api";

interface UseBudgetsParams {
  month?: string; // YYYY-MM format
}

export function useBudgets(params: UseBudgetsParams = {}) {
  return useQuery({
    queryKey: ["budgets", params],
    queryFn: () => budgetsApi.list(params.month),
    staleTime: 30 * 1000,
  });
}

export function useCreateOrUpdateBudget() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { category: string; amount: number }) =>
      budgetsApi.createOrUpdate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
    },
  });
}

export function useUpdateBudget() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ category, amount }: { category: string; amount: number }) =>
      budgetsApi.update(category, { amount }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDeleteBudget() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (category: string) => budgetsApi.delete(category),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
