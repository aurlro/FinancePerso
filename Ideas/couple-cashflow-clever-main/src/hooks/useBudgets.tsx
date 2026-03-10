import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

export interface CategoryBudget {
  id: string;
  household_id: string;
  category_id: string;
  monthly_amount: number;
}

export function useBudgets() {
  return useQuery({
    queryKey: ["category-budgets"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("category_budgets")
        .select("*");
      if (error) throw error;
      return data as CategoryBudget[];
    },
  });
}

export function useUpsertBudget() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (params: { householdId: string; categoryId: string; amount: number }) => {
      const { data: existing } = await supabase
        .from("category_budgets")
        .select("id")
        .eq("household_id", params.householdId)
        .eq("category_id", params.categoryId)
        .maybeSingle();

      if (existing) {
        const { error } = await supabase
          .from("category_budgets")
          .update({ monthly_amount: params.amount })
          .eq("id", existing.id);
        if (error) throw error;
      } else {
        const { error } = await supabase
          .from("category_budgets")
          .insert({ household_id: params.householdId, category_id: params.categoryId, monthly_amount: params.amount });
        if (error) throw error;
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["category-budgets"] });
      toast.success("Budget enregistré");
    },
    onError: () => toast.error("Erreur lors de l'enregistrement"),
  });
}

export function useDeleteBudget() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("category_budgets").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["category-budgets"] });
      toast.success("Budget supprimé");
    },
  });
}
