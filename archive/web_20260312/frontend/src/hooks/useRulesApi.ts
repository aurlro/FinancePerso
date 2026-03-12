/**
 * Hooks React Query pour les Règles de Catégorisation
 * Remplacent les hooks Supabase par des appels API FastAPI
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { rulesApi, type Rule, type RuleTestResult } from "@/lib/api";

export function useRules() {
  return useQuery({
    queryKey: ["rules"],
    queryFn: () => rulesApi.list(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateRule() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { pattern: string; category: string; priority?: number }) =>
      rulesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rules"] });
    },
  });
}

export function useUpdateRule() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Rule> }) =>
      rulesApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["rules"] });
      queryClient.invalidateQueries({ queryKey: ["rule", variables.id] });
    },
  });
}

export function useDeleteRule() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => rulesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rules"] });
    },
  });
}

export function useTestRule() {
  return useMutation({
    mutationFn: (data: { pattern: string; testLabels?: string[] }) =>
      rulesApi.test(data),
  });
}
