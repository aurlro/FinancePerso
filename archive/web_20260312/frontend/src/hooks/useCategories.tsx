/**
 * @file useCategories.tsx
 * @description Hook pour la gestion des catégories - VERSION ADAPTÉE POUR FASTAPI
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export interface Category {
  id: string;
  name: string;
  emoji: string;
  color: string;
  type: "income" | "expense" | "both";
  isFixed?: boolean;
  budgetAmount?: number;
  createdAt: string;
  updatedAt: string;
}

export interface CreateCategoryInput {
  name: string;
  emoji: string;
  color: string;
  type: "income" | "expense" | "both";
  isFixed?: boolean;
  budgetAmount?: number;
}

// ============================================
// MOCK DATA
// ============================================
const MOCK_CATEGORIES: Category[] = [
  { id: "cat-001", name: "Alimentation", emoji: "🍽️", color: "#22c55e", type: "expense", createdAt: "", updatedAt: "" },
  { id: "cat-002", name: "Transport", emoji: "🚗", color: "#3b82f6", type: "expense", createdAt: "", updatedAt: "" },
  { id: "cat-003", name: "Logement", emoji: "🏠", color: "#f59e0b", type: "expense", isFixed: true, createdAt: "", updatedAt: "" },
  { id: "cat-004", name: "Loisirs", emoji: "🎮", color: "#ef4444", type: "expense", createdAt: "", updatedAt: "" },
  { id: "cat-005", name: "Santé", emoji: "💊", color: "#ec4899", type: "expense", createdAt: "", updatedAt: "" },
  { id: "cat-006", name: "Salaire", emoji: "💰", color: "#10b981", type: "income", createdAt: "", updatedAt: "" },
];

// ============================================
// HOOKS
// ============================================

export function useCategories(type?: "income" | "expense") {
  return useQuery({
    queryKey: ["categories", type],
    queryFn: async (): Promise<Category[]> => {
      // TODO: GET /api/categories?type=...
      await new Promise(resolve => setTimeout(resolve, 200));
      
      if (type) {
        return MOCK_CATEGORIES.filter(c => c.type === type || c.type === "both");
      }
      return MOCK_CATEGORIES;
    },
  });
}

export function useCategory(id: string) {
  return useQuery({
    queryKey: ["categories", id],
    queryFn: async (): Promise<Category> => {
      // TODO: GET /api/categories/{id}
      await new Promise(resolve => setTimeout(resolve, 200));
      const cat = MOCK_CATEGORIES.find(c => c.id === id);
      if (!cat) throw new Error("Category not found");
      return cat;
    },
    enabled: !!id,
  });
}

export function useCreateCategory() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (input: CreateCategoryInput): Promise<Category> => {
      // TODO: POST /api/categories
      await new Promise(resolve => setTimeout(resolve, 300));
      
      return {
        ...input,
        id: `cat-${Date.now()}`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });
}

export function useUpdateCategory() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, ...data }: { id: string } & Partial<CreateCategoryInput>): Promise<Category> => {
      // TODO: PUT /api/categories/{id}
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const cat = MOCK_CATEGORIES.find(c => c.id === id);
      if (!cat) throw new Error("Category not found");
      
      return { ...cat, ...data, updatedAt: new Date().toISOString() };
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["categories", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });
}

export function useDeleteCategory() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      // TODO: DELETE /api/categories/{id}
      await new Promise(resolve => setTimeout(resolve, 300));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });
}
