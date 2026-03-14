import { useState, useEffect, useCallback } from 'react';
import { useIPC } from './useIPC';
import type { Subscription, DetectedSubscription } from '../types';

export function useSubscriptions() {
  const { 
    getSubscriptions, 
    createSubscription, 
    updateSubscription, 
    deleteSubscription,
    detectSubscriptions,
    getUpcomingPayments 
  } = useIPC();
  
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSubscriptions = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getSubscriptions();
      setSubscriptions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement des abonnements');
    } finally {
      setIsLoading(false);
    }
  }, [getSubscriptions]);

  const addSubscription = useCallback(async (data: Partial<Subscription>) => {
    setError(null);
    try {
      const newSubscription = await createSubscription(data);
      setSubscriptions(prev => [...prev, newSubscription]);
      return newSubscription;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la création de l\'abonnement');
      throw err;
    }
  }, [createSubscription]);

  const editSubscription = useCallback(async (id: number, data: Partial<Subscription>) => {
    setError(null);
    try {
      const updated = await updateSubscription(id, data);
      setSubscriptions(prev => prev.map(s => s.id === id ? updated : s));
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la mise à jour de l\'abonnement');
      throw err;
    }
  }, [updateSubscription]);

  const removeSubscription = useCallback(async (id: number) => {
    setError(null);
    try {
      await deleteSubscription(id);
      setSubscriptions(prev => prev.filter(s => s.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la suppression de l\'abonnement');
      throw err;
    }
  }, [deleteSubscription]);

  const runDetection = useCallback(async () => {
    setIsDetecting(true);
    setError(null);
    try {
      const detected = await detectSubscriptions();
      return detected as DetectedSubscription[];
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la détection des abonnements');
      throw err;
    } finally {
      setIsDetecting(false);
    }
  }, [detectSubscriptions]);

  useEffect(() => {
    fetchSubscriptions();
  }, [fetchSubscriptions]);

  return {
    subscriptions,
    isLoading,
    isDetecting,
    error,
    fetchSubscriptions,
    addSubscription,
    editSubscription,
    removeSubscription,
    runDetection,
  };
}

export function useUpcomingPayments(days = 7) {
  const { getUpcomingPayments } = useIPC();
  const [upcoming, setUpcoming] = useState<Subscription[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUpcoming = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getUpcomingPayments(days);
      setUpcoming(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement des paiements à venir');
    } finally {
      setIsLoading(false);
    }
  }, [getUpcomingPayments, days]);

  useEffect(() => {
    fetchUpcoming();
  }, [fetchUpcoming]);

  return {
    upcoming,
    isLoading,
    error,
    refetch: fetchUpcoming,
  };
}
