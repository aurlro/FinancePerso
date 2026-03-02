import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import type { Tables } from "@/integrations/supabase/types";

export type CategorizationRule = Tables<"categorization_rules">;

export function useRules() {
  return useQuery({
    queryKey: ["categorization_rules"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("categorization_rules")
        .select("*, categories(*)")
        .order("priority", { ascending: false });
      if (error) throw error;
      return data;
    },
  });
}
