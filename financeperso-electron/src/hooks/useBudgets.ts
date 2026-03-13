import { useState, useEffect, useCallback } from 'react';
import { useIPC } from './useIPC';
import type { Budget, BudgetStatus } from '../types';

export function useBudgets() {
  const { getBudgets, createBudget, updateBudget, deleteBudget } = useIPC();
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBudgets = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getBudgets();
      setBudgets(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement des budgets');
    } finally {
      setIsLoading(false);
    }
  }, [getBudgets]);

  const addBudget = useCallback(async (data: Partial<Budget>) => {
    setError(null);
    try {
      const newBudget = await createBudget(data);
      setBudgets(prev => [...prev, newBudget]);
      return newBudget;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la création du budget');
      throw err;
    }
  }, [createBudget]);

  const editBudget = useCallback(async (id: number, data: Partial<Budget>) => {
    setError(null);
    try {
      const updated = await updateBudget(id, data);
      setBudgets(prev => prev.map(b => b.id === id ? updated : b));
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la mise à jour du budget');
      throw err;
    }
  }, [updateBudget]);

  const removeBudget = useCallback(async (id: number) => {
    setError(null);
    try {
      await deleteBudget(id);
      setBudgets(prev => prev.filter(b => b.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la suppression du budget');
      throw err;
    }
  }, [deleteBudget]);

  useEffect(() => {
    fetchBudgets();
  }, [fetchBudgets]);

  return {
    budgets,
    isLoading,
    error,
    fetchBudgets,
    addBudget,
    editBudget,
    removeBudget,
  };
}

export function useBudgetStatus(year: number, month: number) {
  const { getBudgetStatus } = useIPC();
  const [statuses, setStatuses] = useState<BudgetStatus[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getBudgetStatus(year, month);
      setStatuses(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement du statut des budgets');
    } finally {
      setIsLoading(false);
    }
  }, [getBudgetStatus, year, month]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  return {
    statuses,
    isLoading,
    error,
    refetch: fetchStatus,
  };
}
