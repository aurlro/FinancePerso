import { useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

export function useCreateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (cat: { name: string; color?: string; icon?: string; householdId: string }) => {
      const { error } = await supabase.from("categories").insert({
        name: cat.name,
        color: cat.color || null,
        icon: cat.icon || null,
        household_id: cat.householdId,
        is_default: false,
      });
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categories"] });
      toast.success("Catégorie créée");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useUpdateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, name, color, icon }: { id: string; name: string; color?: string; icon?: string }) => {
      const { error } = await supabase.from("categories").update({ name, color, icon }).eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categories"] });
      toast.success("Catégorie modifiée");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useDeleteCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("categories").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categories"] });
      toast.success("Catégorie supprimée");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
