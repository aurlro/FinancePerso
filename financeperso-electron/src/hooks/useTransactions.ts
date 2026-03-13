import { useState, useEffect, useCallback } from 'react';
import { useElectron } from './useElectron';
import type { Transaction } from '@/types';

interface UseTransactionsOptions {
  year?: number;
  month?: number;
  limit?: number;
}

export function useTransactions(options: UseTransactionsOptions = {}) {
  const { year, month, limit = 100 } = options;
  const electron = useElectron();
  
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTransactions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      let data: Transaction[];
      if (year !== undefined && month !== undefined) {
        data = await electron.getTransactionsByMonth(year, month);
      } else {
        data = await electron.getTransactions({ limit });
      }
      
      setTransactions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de chargement');
    } finally {
      setLoading(false);
    }
  }, [year, month, limit, electron]);

  const addTransaction = useCallback(async (data: Omit<Transaction, 'id'>) => {
    try {
      const newTx = await electron.insertTransaction(data);
      setTransactions(prev => [newTx, ...prev]);
      return newTx;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Erreur d\'ajout');
    }
  }, [electron]);

  const updateTransaction = useCallback(async (id: number, data: Partial<Transaction>) => {
    try {
      const updated = await electron.updateTransaction(id, data);
      setTransactions(prev => 
        prev.map(tx => tx.id === id ? { ...tx, ...updated } : tx)
      );
      return updated;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Erreur de mise à jour');
    }
  }, [electron]);

  const removeTransaction = useCallback(async (id: number) => {
    try {
      await electron.deleteTransaction(id);
      setTransactions(prev => prev.filter(tx => tx.id !== id));
    } catch (err) {
      throw err instanceof Error ? err : new Error('Erreur de suppression');
    }
  }, [electron]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  return {
    transactions,
    loading,
    error,
    refresh: fetchTransactions,
    addTransaction,
    updateTransaction,
    removeTransaction,
  };
}
