import { useState, useEffect, useCallback } from 'react';
import { useIPC } from './useIPC';
import type { Transaction } from '../types';

export function useValidation() {
  const [pendingTransactions, setPendingTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getPendingTransactions, validateBatch: validateBatchAPI, ignoreTransactions: ignoreTransactionsAPI } = useIPC();

  const fetchPendingTransactions = useCallback(async () => {
    try {
      setLoading(true);
      const results = await getPendingTransactions();
      setPendingTransactions(results);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  }, [getPendingTransactions]);

  const validateBatch = useCallback(async (ids: number[], category: string) => {
    try {
      await validateBatchAPI(ids, category);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la validation');
      return false;
    }
  }, [validateBatchAPI]);

  const ignoreTransactions = useCallback(async (ids: number[]) => {
    try {
      await ignoreTransactionsAPI(ids);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de l\'ignorance');
      return false;
    }
  }, [ignoreTransactionsAPI]);

  useEffect(() => {
    fetchPendingTransactions();
  }, [fetchPendingTransactions]);

  return {
    pendingTransactions,
    loading,
    error,
    refresh: fetchPendingTransactions,
    validateBatch,
    ignoreTransactions,
  };
}
