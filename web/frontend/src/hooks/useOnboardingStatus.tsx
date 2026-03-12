import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { useAccounts } from "@/hooks/useAccounts";
import { useTransactions } from "@/hooks/useTransactionsApi";

/**
 * Hook pour gérer le statut de l'onboarding
 * Détecte si l'utilisateur a besoin de compléter l'onboarding
 * basé sur la présence de comptes et de transactions
 */
export function useOnboardingStatus() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  // Vérifier si l'onboarding a été complété dans le localStorage
  const onboardingCompleted = localStorage.getItem('onboarding-completed') === 'true';
  
  const { data: accounts, isLoading: loadingAccounts } = useAccounts();
  
  const { data: transactionsData, isLoading: loadingTx } = useTransactions({
    limit: 1,
  });

  const isLoading = loadingAccounts || loadingTx;
  const hasAccounts = (accounts?.length ?? 0) > 0;
  const hasTransactions = (transactionsData?.items?.length ?? 0) > 0 || (transactionsData?.total ?? 0) > 0;
  
  // Onboarding nécessaire si pas complété et pas de données
  const needsOnboarding = !onboardingCompleted && !isLoading && (!hasAccounts || !hasTransactions);
  
  const initialStep = 1;

  const markOnboardingComplete = useMutation({
    mutationFn: async () => {
      localStorage.setItem('onboarding-completed', 'true');
      return true;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["onboarding-status"] });
    },
  });

  return { 
    needsOnboarding, 
    isLoading, 
    hasAccounts, 
    hasTransactions, 
    initialStep, 
    markOnboardingComplete 
  };
}
