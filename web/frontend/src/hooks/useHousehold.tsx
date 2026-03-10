/**
 * @file useHousehold.tsx
 * @description Hook pour la gestion des membres du foyer - VERSION ADAPTÉE POUR FASTAPI
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export interface HouseholdMember {
  id: string;
  name: string;
  email?: string;
  role: "owner" | "member" | "viewer";
  avatarUrl?: string;
  color: string;
  incomeShare?: number;
  expenseShare?: number;
  createdAt: string;
  updatedAt: string;
}

export interface CreateMemberInput {
  name: string;
  email?: string;
  role?: "owner" | "member" | "viewer";
  color?: string;
  incomeShare?: number;
  expenseShare?: number;
}

// ============================================
// MOCK DATA - À remplacer par appels API réels
// ============================================
const MOCK_MEMBERS: HouseholdMember[] = [
  {
    id: "mem-1",
    name: "Moi",
    role: "owner",
    color: "#10b981",
    incomeShare: 50,
    expenseShare: 50,
    createdAt: "2024-01-01T00:00:00Z",
    updatedAt: "2024-01-01T00:00:00Z",
  },
  {
    id: "mem-2", 
    name: "Partenaire",
    role: "member",
    color: "#3b82f6",
    incomeShare: 50,
    expenseShare: 50,
    createdAt: "2024-01-01T00:00:00Z",
    updatedAt: "2024-01-01T00:00:00Z",
  },
];

// ============================================
// HOOKS
// ============================================

export function useHouseholdMembers() {
  return useQuery({
    queryKey: ["household", "members"],
    queryFn: async (): Promise<HouseholdMember[]> => {
      // TODO: GET /api/household/members
      await new Promise(resolve => setTimeout(resolve, 300));
      return MOCK_MEMBERS;
    },
  });
}

// Alias pour compatibilité avec les composants qui importent useHousehold
export const useHousehold = useHouseholdMembers;

export function useAddMember() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (input: CreateMemberInput): Promise<HouseholdMember> => {
      // TODO: POST /api/household/members
      await new Promise(resolve => setTimeout(resolve, 300));
      
      return {
        ...input,
        id: `mem-${Date.now()}`,
        role: input.role || "member",
        color: input.color || "#6b7280",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household", "members"] });
    },
  });
}

export function useUpdateMember() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, ...data }: { id: string } & Partial<CreateMemberInput>): Promise<HouseholdMember> => {
      // TODO: PUT /api/household/members/{id}
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const member = MOCK_MEMBERS.find(m => m.id === id);
      if (!member) throw new Error("Member not found");
      
      return { ...member, ...data, updatedAt: new Date().toISOString() };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household", "members"] });
    },
  });
}

export function useDeleteMember() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      // TODO: DELETE /api/household/members/{id}
      await new Promise(resolve => setTimeout(resolve, 300));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household", "members"] });
    },
  });
}

// Exports additionnels pour compatibilité
export const useUpdateHousehold = useUpdateMember;
export const useAddGhostMember = useAddMember;
export function useSendInvitation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (_email: string): Promise<void> => {
      // TODO: POST /api/household/invite
      await new Promise(resolve => setTimeout(resolve, 300));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household"] });
    },
  });
}
export const useUpdateMemberCard = useUpdateMember;
export const useHouseholdId = () => "household-1";
export const useUpdateHouseholdId = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (_id: string) => {
      await new Promise(resolve => setTimeout(resolve, 300));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household"] });
    },
  });
};
export const useUpdateProfile = useUpdateMember;
export const useLeaveHousehold = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 300));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household"] });
    },
  });
};
export const useInvitations = () => {
  return useQuery({
    queryKey: ["household", "invitations"],
    queryFn: async () => [],
  });
};
export const useCancelInvitation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (_id: string) => {
      await new Promise(resolve => setTimeout(resolve, 300));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household", "invitations"] });
    },
  });
};
export const useDeleteInvitation = useCancelInvitation;
export const useAcceptInvitation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (_token: string) => {
      await new Promise(resolve => setTimeout(resolve, 300));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household"] });
    },
  });
};
export const useUpdateGhostMember = useUpdateMember;
export const useRemoveMember = useDeleteMember;
export const useDeleteGhostMember = useDeleteMember;
export const useToggleMemberActive = useUpdateMember;
