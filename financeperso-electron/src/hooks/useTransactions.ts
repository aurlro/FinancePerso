import { useState, useEffect, useCallback } from 'react';
import { useIPC } from './useIPC';
import type { Transaction, DashboardStats, CategoryStat } from '../types';

export function useTransactions(limit = 100) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getAllTransactions, createTransaction: createTxAPI } = useIPC();

  const fetchTransactions = useCallback(async () => {
    try {
      setLoading(true);
      const results = await getAllTransactions(limit, 0);
      setTransactions(results);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  }, [getAllTransactions, limit]);

  const addTransaction = useCallback(async (transaction: Omit<Transaction, 'id'>) => {
    try {
      await createTxAPI(transaction);
      await fetchTransactions();
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de l\'ajout');
      return false;
    }
  }, [createTxAPI, fetchTransactions]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  return {
    transactions,
    loading,
    error,
    refresh: fetchTransactions,
    addTransaction,
  };
}

export function useDashboardStats(year: number, month: number) {
  const [stats, setStats] = useState<DashboardStats>({
    income: 0,
    expense: 0,
    balance: 0,
  });
  const [categoryStats, setCategoryStats] = useState<CategoryStat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getStatsByMonth, getCategoriesStats } = useIPC();

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      
      const [monthStats, catStats] = await Promise.all([
        getStatsByMonth(year, month),
        getCategoriesStats(year, month),
      ]);

      // Calculer les totaux
      let income = 0;
      let expense = 0;

      for (const stat of monthStats) {
        if (stat.type === 'income') {
          income = stat.total || 0;
        } else if (stat.type === 'expense') {
          expense = stat.total || 0;
        }
      }

      setStats({
        income,
        expense,
        balance: income - expense,
      });
      
      setCategoryStats(catStats);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  }, [getStatsByMonth, getCategoriesStats, year, month]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    categoryStats,
    loading,
    error,
    refresh: fetchStats,
  };
}

export function useCategories() {
  const [categories, setCategories] = useState<Array<{ id: number; name: string; emoji: string; color: string }>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getCategories } = useIPC();

  const fetchCategories = useCallback(async () => {
    try {
      setLoading(true);
      const results = await getCategories();
      setCategories(results);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  }, [getCategories]);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  return {
    categories,
    loading,
    error,
    refresh: fetchCategories,
  };
}
