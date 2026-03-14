import { useState, useEffect, useCallback, useMemo } from 'react';
import { useIPC } from './useIPC';
import type { WealthAccount, SavingsGoal, ProjectionResult, SimulatorConfig } from '../types/wealth';

// Fonction utilitaire pour calculer les projections
function calculateProjections(
  initial: number,
  monthly: number,
  rate: number,
  years: number
): ProjectionResult {
  const monthlyRate = rate / 12 / 100;
  const months = years * 12;
  const monthlyData = [];
  
  let currentAmount = initial;
  let totalContributions = initial;
  let totalInterest = 0;
  
  const startDate = new Date();
  
  for (let i = 0; i < months; i++) {
    const interest = currentAmount * monthlyRate;
    currentAmount += monthly + interest;
    totalContributions += monthly;
    totalInterest += interest;
    
    const date = new Date(startDate.getFullYear(), startDate.getMonth() + i + 1, 1);
    
    monthlyData.push({
      month: i + 1,
      year: date.getFullYear(),
      amount: Math.round(currentAmount * 100) / 100,
      contributions: Math.round(totalContributions * 100) / 100,
      interest: Math.round(totalInterest * 100) / 100,
    });
  }
  
  return {
    finalAmount: Math.round(currentAmount * 100) / 100,
    totalContributions: Math.round(totalContributions * 100) / 100,
    totalInterest: Math.round(totalInterest * 100) / 100,
    monthlyData,
  };
}

// Hook pour gérer les comptes de patrimoine
export function useWealthAccounts() {
  const { getWealthAccounts, createWealthAccount, updateWealthAccount, deleteWealthAccount } = useIPC();
  const [accounts, setAccounts] = useState<WealthAccount[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAccounts = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getWealthAccounts();
      setAccounts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement des comptes');
    } finally {
      setIsLoading(false);
    }
  }, [getWealthAccounts]);

  const addAccount = useCallback(async (data: Partial<WealthAccount>) => {
    setError(null);
    try {
      const newAccount = await createWealthAccount(data);
      setAccounts(prev => [...prev, newAccount]);
      return newAccount;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la création du compte');
      throw err;
    }
  }, [createWealthAccount]);

  const editAccount = useCallback(async (id: number, data: Partial<WealthAccount>) => {
    setError(null);
    try {
      const updated = await updateWealthAccount(id, data);
      setAccounts(prev => prev.map(a => a.id === id ? updated : a));
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la mise à jour du compte');
      throw err;
    }
  }, [updateWealthAccount]);

  const removeAccount = useCallback(async (id: number) => {
    setError(null);
    try {
      await deleteWealthAccount(id);
      setAccounts(prev => prev.filter(a => a.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la suppression du compte');
      throw err;
    }
  }, [deleteWealthAccount]);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  // Calcul des statistiques
  const stats = useMemo(() => {
    const totalWealth = accounts.reduce((sum, a) => sum + (a.balance || 0), 0);
    const totalChecking = accounts
      .filter(a => a.type === 'checking')
      .reduce((sum, a) => sum + (a.balance || 0), 0);
    const totalSavings = accounts
      .filter(a => a.type === 'savings')
      .reduce((sum, a) => sum + (a.balance || 0), 0);
    const totalInvestments = accounts
      .filter(a => a.type === 'investment')
      .reduce((sum, a) => sum + (a.balance || 0), 0);
    const totalCrypto = accounts
      .filter(a => a.type === 'crypto')
      .reduce((sum, a) => sum + (a.balance || 0), 0);

    return {
      totalWealth,
      totalChecking,
      totalSavings,
      totalInvestments,
      totalCrypto,
      monthlyChange: 0, // TODO: calculer à partir de l'historique
      yearlyChange: 0,
    };
  }, [accounts]);

  // Distribution pour le pie chart
  const distribution = useMemo(() => {
    const total = stats.totalWealth;
    if (total === 0) return [];

    const colors = {
      checking: '#3b82f6',   // blue
      savings: '#10b981',    // emerald
      investment: '#8b5cf6', // violet
      crypto: '#f59e0b',     // amber
      other: '#6b7280',      // gray
    };

    return [
      { type: 'checking' as const, amount: stats.totalChecking, percentage: (stats.totalChecking / total) * 100, color: colors.checking },
      { type: 'savings' as const, amount: stats.totalSavings, percentage: (stats.totalSavings / total) * 100, color: colors.savings },
      { type: 'investment' as const, amount: stats.totalInvestments, percentage: (stats.totalInvestments / total) * 100, color: colors.investment },
      { type: 'crypto' as const, amount: stats.totalCrypto, percentage: (stats.totalCrypto / total) * 100, color: colors.crypto },
    ].filter(d => d.amount > 0);
  }, [stats]);

  return {
    accounts,
    stats,
    distribution,
    isLoading,
    error,
    fetchAccounts,
    addAccount,
    editAccount,
    removeAccount,
  };
}

// Hook pour gérer les objectifs d'épargne
export function useSavingsGoals() {
  const { getSavingsGoals, createSavingsGoal, updateSavingsGoal, deleteSavingsGoal } = useIPC();
  const [goals, setGoals] = useState<SavingsGoal[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchGoals = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getSavingsGoals();
      setGoals(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement des objectifs');
    } finally {
      setIsLoading(false);
    }
  }, [getSavingsGoals]);

  const addGoal = useCallback(async (data: Partial<SavingsGoal>) => {
    setError(null);
    try {
      // Calculer la contribution mensuelle suggérée si deadline est fournie
      if (data.deadline && data.target_amount && !data.monthly_contribution) {
        const deadline = new Date(data.deadline);
        const now = new Date();
        const months = Math.max(1, (deadline.getFullYear() - now.getFullYear()) * 12 + 
          (deadline.getMonth() - now.getMonth()));
        const remaining = data.target_amount - (data.current_amount || 0);
        data.monthly_contribution = Math.round((remaining / months) * 100) / 100;
      }

      const newGoal = await createSavingsGoal(data);
      setGoals(prev => [...prev, newGoal]);
      return newGoal;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la création de l\'objectif');
      throw err;
    }
  }, [createSavingsGoal]);

  const editGoal = useCallback(async (id: number, data: Partial<SavingsGoal>) => {
    setError(null);
    try {
      const updated = await updateSavingsGoal(id, data);
      setGoals(prev => prev.map(g => g.id === id ? updated : g));
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la mise à jour de l\'objectif');
      throw err;
    }
  }, [updateSavingsGoal]);

  const removeGoal = useCallback(async (id: number) => {
    setError(null);
    try {
      await deleteSavingsGoal(id);
      setGoals(prev => prev.filter(g => g.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la suppression de l\'objectif');
      throw err;
    }
  }, [deleteSavingsGoal]);

  // Mettre à jour le montant actuel d'un objectif
  const contributeToGoal = useCallback(async (id: number, amount: number) => {
    const goal = goals.find(g => g.id === id);
    if (!goal) return;

    const newAmount = (goal.current_amount || 0) + amount;
    await editGoal(id, { current_amount: newAmount });
  }, [goals, editGoal]);

  useEffect(() => {
    fetchGoals();
  }, [fetchGoals]);

  return {
    goals,
    isLoading,
    error,
    fetchGoals,
    addGoal,
    editGoal,
    removeGoal,
    contributeToGoal,
  };
}

// Hook pour les projections
export function useProjections(config: SimulatorConfig) {
  return useMemo(() => {
    return calculateProjections(
      config.initialAmount,
      config.monthlyContribution,
      config.annualRate,
      config.years
    );
  }, [config.initialAmount, config.monthlyContribution, config.annualRate, config.years]);
}

// Hook pour calculer la contribution mensuelle suggérée
export function useSuggestedContribution(targetAmount: number, deadline: string, currentAmount = 0) {
  return useMemo(() => {
    const deadlineDate = new Date(deadline);
    const now = new Date();
    const months = Math.max(1, (deadlineDate.getFullYear() - now.getFullYear()) * 12 + 
      (deadlineDate.getMonth() - now.getMonth()));
    const remaining = targetAmount - currentAmount;
    return Math.max(0, Math.round((remaining / months) * 100) / 100);
  }, [targetAmount, deadline, currentAmount]);
}
