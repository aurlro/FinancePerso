/**
 * Hooks React Query pour les Catégories
 * Remplacent les hooks Supabase par des appels API FastAPI
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { categoriesApi, type Category } from "@/lib/api";

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: () => categoriesApi.list(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateCategory() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { name: string; emoji?: string; is_fixed?: number; suggested_tags?: string }) =>
      categoriesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });
}

export function useUpdateCategory() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Category> }) =>
      categoriesApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      queryClient.invalidateQueries({ queryKey: ["category", variables.id] });
    },
  });
}

export function useDeleteCategory() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => categoriesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });
}
