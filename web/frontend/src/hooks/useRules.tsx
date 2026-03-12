/**
 * @file useRules.tsx
 * @description Hook pour la gestion des règles de catégorisation - VERSION ADAPTÉE POUR FASTAPI
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export interface AttributionRule {
  id: string;
  name: string;
  pattern: string;
  patternType: "contains" | "regex" | "exact" | "starts_with" | "ends_with";
  categoryId: string;
  categoryName?: string;
  memberId?: string;
  memberName?: string;
  priority: number;
  isActive: boolean;
  matchCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface CreateRuleInput {
  name: string;
  pattern: string;
  patternType: "contains" | "regex" | "exact" | "starts_with" | "ends_with";
  categoryId: string;
  memberId?: string;
  priority?: number;
}

// ============================================
// MOCK DATA
// ============================================
const MOCK_RULES: AttributionRule[] = [
  {
    id: "rule-001",
    name: "Supermarchés",
    pattern: "CARREFOUR|CASINO|LIDL|AUCHAN",
    patternType: "regex",
    categoryId: "cat-001",
    categoryName: "Alimentation",
    priority: 10,
    isActive: true,
    matchCount: 45,
    createdAt: "",
    updatedAt: "",
  },
  {
    id: "rule-002",
    name: "Transport",
    pattern: "TOTAL|ESSO|SHELL",
    patternType: "regex",
    categoryId: "cat-002",
    categoryName: "Transport",
    priority: 10,
    isActive: true,
    matchCount: 23,
    createdAt: "",
    updatedAt: "",
  },
];

// ============================================
// HOOKS
// ============================================

export function useRules() {
  return useQuery({
    queryKey: ["rules"],
    queryFn: async (): Promise<AttributionRule[]> => {
      // TODO: GET /api/rules
      await new Promise(resolve => setTimeout(resolve, 200));
      return MOCK_RULES;
    },
  });
}

export function useRule(id: string) {
  return useQuery({
    queryKey: ["rules", id],
    queryFn: async (): Promise<AttributionRule> => {
      // TODO: GET /api/rules/{id}
      await new Promise(resolve => setTimeout(resolve, 200));
      const rule = MOCK_RULES.find(r => r.id === id);
      if (!rule) throw new Error("Rule not found");
      return rule;
    },
    enabled: !!id,
  });
}

export function useCreateRule() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (input: CreateRuleInput): Promise<AttributionRule> => {
      // TODO: POST /api/rules
      await new Promise(resolve => setTimeout(resolve, 300));
      
      return {
        ...input,
        id: `rule-${Date.now()}`,
        priority: input.priority || 10,
        isActive: true,
        matchCount: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rules"] });
    },
  });
}

export function useUpdateRule() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, ...data }: { id: string } & Partial<CreateRuleInput>): Promise<AttributionRule> => {
      // TODO: PUT /api/rules/{id}
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const rule = MOCK_RULES.find(r => r.id === id);
      if (!rule) throw new Error("Rule not found");
      
      return { ...rule, ...data, updatedAt: new Date().toISOString() };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rules"] });
    },
  });
}

export function useDeleteRule() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      // TODO: DELETE /api/rules/{id}
      await new Promise(resolve => setTimeout(resolve, 300));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rules"] });
    },
  });
}

export function useTestRule() {
  return useMutation({
    mutationFn: async ({ pattern, patternType, testText }: { 
      pattern: string; 
      patternType: string; 
      testText: string;
    }): Promise<boolean> => {
      // TODO: POST /api/rules/test
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Simulation simple
      if (patternType === "contains") {
        return testText.toLowerCase().includes(pattern.toLowerCase());
      }
      if (patternType === "regex") {
        try {
          const regex = new RegExp(pattern, "i");
          return regex.test(testText);
        } catch {
          return false;
        }
      }
      return false;
    },
  });
}
