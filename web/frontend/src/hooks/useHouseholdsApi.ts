/**
 * Hooks React Query pour les Households (PR #7)
 * Gestion des foyers, membres et invitations
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { householdsApi, type Household, type HouseholdMember, type Invitation } from "@/lib/api";

// Hook pour récupérer le household de l'utilisateur
export function useMyHousehold() {
  return useQuery({
    queryKey: ["household", "my"],
    queryFn: () => householdsApi.getMyHousehold(),
    staleTime: 5 * 60 * 1000,
  });
}

// Hook pour créer un household
export function useCreateHousehold() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      householdsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household"] });
      queryClient.invalidateQueries({ queryKey: ["user"] });
    },
  });
}

// Hook pour mettre à jour un household
export function useUpdateHousehold() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: { name?: string; description?: string } }) =>
      householdsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household"] });
    },
  });
}

// Hook pour supprimer un household
export function useDeleteHousehold() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => householdsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household"] });
      queryClient.invalidateQueries({ queryKey: ["user"] });
    },
  });
}

// Hook pour lister les membres d'un household
export function useHouseholdMembers(householdId: number | null) {
  return useQuery({
    queryKey: ["household", householdId, "members"],
    queryFn: () => householdsApi.listMembers(householdId!),
    enabled: !!householdId,
    staleTime: 5 * 60 * 1000,
  });
}

// Hook pour supprimer un membre
export function useRemoveHouseholdMember() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ householdId, userId }: { householdId: number; userId: number }) =>
      householdsApi.removeMember(householdId, userId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["household", variables.householdId, "members"] });
    },
  });
}

// Hook pour créer une invitation
export function useCreateInvitation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ householdId, data }: { householdId: number; data: { email: string; role?: string } }) =>
      householdsApi.createInvitation(householdId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["household", variables.householdId, "invitations"] });
    },
  });
}

// Hook pour lister les invitations
export function useHouseholdInvitations(householdId: number | null) {
  return useQuery({
    queryKey: ["household", householdId, "invitations"],
    queryFn: () => householdsApi.listInvitations(householdId!),
    enabled: !!householdId,
    staleTime: 60 * 1000,
  });
}

// Hook pour accepter une invitation
export function useAcceptInvitation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (token: string) => householdsApi.acceptInvitation(token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household"] });
      queryClient.invalidateQueries({ queryKey: ["user"] });
    },
  });
}

// Hook pour refuser une invitation
export function useDeclineInvitation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (token: string) => householdsApi.declineInvitation(token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household"] });
    },
  });
}

// Hook pour annuler une invitation
export function useCancelInvitation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ householdId, invitationId }: { householdId: number; invitationId: number }) =>
      householdsApi.cancelInvitation(householdId, invitationId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["household", variables.householdId, "invitations"] });
    },
  });
}
