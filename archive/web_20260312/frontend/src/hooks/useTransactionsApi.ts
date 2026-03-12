/**
 * Hooks React Query pour les Transactions
 * Remplacent les hooks Supabase par des appels API FastAPI
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { transactionsApi, type Transaction } from "@/lib/api";

interface UseTransactionsParams {
  limit?: number;
  offset?: number;
  category?: string;
  month?: string;
  status?: string;
  search?: string;
}

export function useTransactions(params: UseTransactionsParams = {}) {
  return useQuery({
    queryKey: ["transactions", params],
    queryFn: () => transactionsApi.list(params),
    staleTime: 30 * 1000, // 30 secondes
  });
}

export function useTransaction(id: number | null) {
  return useQuery({
    queryKey: ["transaction", id],
    queryFn: () => transactionsApi.getById(id!),
    enabled: !!id,
  });
}

export function useUpdateTransaction() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Transaction> }) =>
      transactionsApi.update(id, data),
    onSuccess: (_, variables) => {
      // Invalider les caches concernés
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["transaction", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useCategorizeTransactions() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (ids: number[]) => transactionsApi.categorize(ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useBulkUpdateStatus() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ ids, status }: { ids: number[]; status: string }) =>
      transactionsApi.bulkUpdateStatus(ids, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDeleteTransaction() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => transactionsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
