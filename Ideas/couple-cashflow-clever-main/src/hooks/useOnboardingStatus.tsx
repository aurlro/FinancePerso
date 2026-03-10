import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { useAccounts } from "@/hooks/useAccounts";

export function useOnboardingStatus() {
  const { user } = useAuth();
  const { data: accounts, isLoading: loadingAccounts } = useAccounts();

  const { data: profile, isLoading: loadingProfile } = useQuery({
    queryKey: ["profile-onboarding", user?.id],
    enabled: !!user,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("profiles")
        .select("onboarding_completed_at")
        .eq("id", user!.id)
        .single();
      if (error) throw error;
      return data;
    },
  });

  const { data: txCount, isLoading: loadingTx } = useQuery({
    queryKey: ["transaction-count", user?.id],
    enabled: !!user && !profile?.onboarding_completed_at,
    queryFn: async () => {
      const { count, error } = await supabase
        .from("transactions")
        .select("id", { count: "exact", head: true });
      if (error) throw error;
      return count ?? 0;
    },
  });

  const queryClient = useQueryClient();

  const markOnboardingComplete = useMutation({
    mutationFn: async () => {
      const { error } = await supabase
        .from("profiles")
        .update({ onboarding_completed_at: new Date().toISOString() } as any)
        .eq("id", user!.id);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile-onboarding"] });
    },
  });

  const isLoading = loadingProfile || loadingAccounts || loadingTx;

  // If onboarding already completed, skip everything
  if (profile?.onboarding_completed_at) {
    return { needsOnboarding: false, isLoading: loadingProfile, hasAccounts: true, hasTransactions: true, initialStep: 1, markOnboardingComplete };
  }

  const hasAccounts = (accounts?.length ?? 0) > 0;
  const hasTransactions = (txCount ?? 0) > 0;
  const needsOnboarding = !isLoading && (!hasAccounts || !hasTransactions);
  const initialStep = 1;

  return { needsOnboarding, isLoading, hasAccounts, hasTransactions, initialStep, markOnboardingComplete };
}
