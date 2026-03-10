import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";

export interface SavingsGoal {
  id: string;
  household_id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  deadline: string | null;
  icon: string | null;
  color: string;
  is_completed: boolean;
  created_at: string;
}

export function useSavingsGoals() {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["savings-goals"],
    enabled: !!user,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("savings_goals")
        .select("*")
        .order("is_completed", { ascending: true })
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data as SavingsGoal[];
    },
  });
}

export function useAddSavingsGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (goal: { householdId: string; name: string; targetAmount: number; deadline?: string; color?: string }) => {
      const { error } = await supabase.from("savings_goals").insert({
        household_id: goal.householdId,
        name: goal.name,
        target_amount: goal.targetAmount,
        deadline: goal.deadline || null,
        color: goal.color || "#3b82f6",
      });
      if (error) throw error;
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["savings-goals"] }); toast.success("Objectif créé"); },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useUpdateSavingsGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...updates }: { id: string; current_amount?: number; is_completed?: boolean; name?: string; target_amount?: number }) => {
      const { error } = await supabase.from("savings_goals").update(updates).eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["savings-goals"] }); },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useDeleteSavingsGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("savings_goals").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["savings-goals"] }); toast.success("Objectif supprimé"); },
    onError: (e: Error) => toast.error(e.message),
  });
}
