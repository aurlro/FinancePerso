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
  isActive: boolean; // Ajout du statut actif/non-actif
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
  isActive?: boolean;
}

// ============================================
// MOCK DATA - Démarrage avec l'utilisateur actif (connecté) par défaut
// ============================================
let MOCK_MEMBERS: HouseholdMember[] = [
  {
    id: "mem-owner",
    name: "Moi",
    role: "owner",
    color: "#10b981",
    isActive: true, // Actif = se connecte à l'app
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }
];

// ============================================
// HOOKS
// ============================================

export function useHouseholdMembers() {
  return useQuery({
    queryKey: ["household", "members"],
    queryFn: async (): Promise<HouseholdMember[]> => {
      // TODO: GET /api/household/members
      return MOCK_MEMBERS;
    },
  });
}

// Alias pour compatibilité
export const useHousehold = useHouseholdMembers;

export function useAddMember() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (input: CreateMemberInput): Promise<HouseholdMember> => {
      // TODO: POST /api/household/members
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const newMember: HouseholdMember = {
        ...input,
        id: `mem-${Date.now()}`,
        role: input.role || "member",
        color: input.color || "#6b7280",
        isActive: input.isActive ?? true, // Par défaut actif
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      MOCK_MEMBERS.push(newMember);
      return newMember;
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
      
      const idx = MOCK_MEMBERS.findIndex(m => m.id === id);
      if (idx === -1) throw new Error("Member not found");
      
      MOCK_MEMBERS[idx] = { 
        ...MOCK_MEMBERS[idx], 
        ...data, 
        updatedAt: new Date().toISOString() 
      };
      
      return MOCK_MEMBERS[idx];
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
      MOCK_MEMBERS = MOCK_MEMBERS.filter(m => m.id !== id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household", "members"] });
    },
  });
}

// Hook pour activer/désactiver un membre
export function useToggleMemberActive() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, isActive }: { id: string; isActive: boolean }): Promise<void> => {
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const idx = MOCK_MEMBERS.findIndex(m => m.id === id);
      if (idx === -1) throw new Error("Member not found");
      
      MOCK_MEMBERS[idx].isActive = isActive;
      MOCK_MEMBERS[idx].updatedAt = new Date().toISOString();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household", "members"] });
    },
  });
}

// Exports pour compatibilité
export const useUpdateHousehold = useUpdateMember;
export const useAddGhostMember = useAddMember;
export const useSendInvitation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (_email: string) => {
      await new Promise(resolve => setTimeout(resolve, 300));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["household"] });
    },
  });
};
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
