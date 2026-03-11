/**
 * Hooks React Query pour les Membres
 * Remplacent les hooks Supabase par des appels API FastAPI
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { membersApi, type Member } from "@/lib/api";

export function useMembers() {
  return useQuery({
    queryKey: ["members"],
    queryFn: () => membersApi.list(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateMember() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { name: string; member_type?: string }) =>
      membersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["members"] });
    },
  });
}

export function useUpdateMember() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Member> }) =>
      membersApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["member", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
    },
  });
}

export function useDeleteMember() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => membersApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["members"] });
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
    },
  });
}
