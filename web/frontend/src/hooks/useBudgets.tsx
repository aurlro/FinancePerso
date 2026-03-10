/**
 * @file useBudgets.tsx
 * @description Hook pour la gestion des budgets - VERSION ADAPTÉE POUR FASTAPI
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export interface Budget {
  id: string;
  categoryId: string;
  categoryName: string;
  categoryEmoji: string;
  amount: number;
  spent: number;
  remaining: number;
  percentageUsed: number;
  period: "monthly" | "yearly" | "weekly";
  alertThreshold: number;
  isAlertTriggered: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateBudgetInput {
  categoryId: string;
  amount: number;
  period?: "monthly" | "yearly" | "weekly";
  alertThreshold?: number;
}

// ============================================
// MOCK DATA
// ============================================
const MOCK_BUDGETS: Budget[] = [
  {
    id: "bud-001",
    categoryId: "cat-001",
    categoryName: "Alimentation",
    categoryEmoji: "🍽️",
    amount: 500,
    spent: 425,
    remaining: 75,
    percentageUsed: 85,
    period: "monthly",
    alertThreshold: 80,
    isAlertTriggered: true,
    createdAt: "",
    updatedAt: "",
  },
  {
    id: "bud-002",
    categoryId: "cat-002",
    categoryName: "Transport",
    categoryEmoji: "🚗",
    amount: 200,
    spent: 150,
    remaining: 50,
    percentageUsed: 75,
    period: "monthly",
    alertThreshold: 80,
    isAlertTriggered: false,
    createdAt: "",
    updatedAt: "",
  },
];

// ============================================
// HOOKS
// ============================================

export function useBudgets() {
  return useQuery({
    queryKey: ["budgets"],
    queryFn: async (): Promise<Budget[]> => {
      // TODO: GET /api/budgets
      await new Promise(resolve => setTimeout(resolve, 200));
      return MOCK_BUDGETS;
    },
  });
}

export function useBudget(id: string) {
  return useQuery({
    queryKey: ["budgets", id],
    queryFn: async (): Promise<Budget> => {
      // TODO: GET /api/budgets/{id}
      await new Promise(resolve => setTimeout(resolve, 200));
      const bud = MOCK_BUDGETS.find(b => b.id === id);
      if (!bud) throw new Error("Budget not found");
      return bud;
    },
    enabled: !!id,
  });
}

export function useCreateBudget() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (input: CreateBudgetInput): Promise<Budget> => {
      // TODO: POST /api/budgets
      await new Promise(resolve => setTimeout(resolve, 300));
      
      return {
        ...input,
        id: `bud-${Date.now()}`,
        categoryName: "Nouvelle catégorie",
        categoryEmoji: "📦",
        spent: 0,
        remaining: input.amount,
        percentageUsed: 0,
        period: input.period || "monthly",
        alertThreshold: input.alertThreshold || 80,
        isAlertTriggered: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useUpdateBudget() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, ...data }: { id: string } & Partial<CreateBudgetInput>): Promise<Budget> => {
      // TODO: PUT /api/budgets/{id}
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const bud = MOCK_BUDGETS.find(b => b.id === id);
      if (!bud) throw new Error("Budget not found");
      
      return { ...bud, ...data, updatedAt: new Date().toISOString() };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDeleteBudget() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      // TODO: DELETE /api/budgets/{id}
      await new Promise(resolve => setTimeout(resolve, 300));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

// Alias pour compatibilité
export const useUpsertBudget = useUpdateBudget;
