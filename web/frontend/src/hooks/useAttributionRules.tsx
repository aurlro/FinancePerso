import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export function useAttributionRules() {
  return useQuery({
    queryKey: ["attribution_rules"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("attribution_rules")
        .select("*, household_members(display_name)")
        .order("priority", { ascending: false });
      if (error) throw error;
      return data;
    },
  });
}
