import { useState, useEffect, useCallback } from 'react';
import { useIPC } from './useIPC';
import type { Member, MemberStats, Transaction } from '../types';

const DEFAULT_MEMBER_COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];
const DEFAULT_MEMBER_EMOJIS = ['👤', '👥', '👨', '👩', '🧑', '🙂'];

export function useMembers() {
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getMembers, createMember: createMemberAPI, updateMember: updateMemberAPI, deleteMember: deleteMemberAPI } = useIPC();

  const fetchMembers = useCallback(async () => {
    try {
      setLoading(true);
      const results = await getMembers();
      setMembers(results);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement des membres');
    } finally {
      setLoading(false);
    }
  }, [getMembers]);

  const addMember = useCallback(async (data: Omit<Member, 'id' | 'is_active' | 'created_at'>) => {
    try {
      await createMemberAPI(data);
      await fetchMembers();
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de l\'ajout du membre');
      return false;
    }
  }, [createMemberAPI, fetchMembers]);

  const updateMember = useCallback(async (id: number, data: Partial<Member>) => {
    try {
      await updateMemberAPI(id, data);
      await fetchMembers();
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la mise à jour');
      return false;
    }
  }, [updateMemberAPI, fetchMembers]);

  const removeMember = useCallback(async (id: number) => {
    try {
      await deleteMemberAPI(id);
      await fetchMembers();
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la suppression');
      return false;
    }
  }, [deleteMemberAPI, fetchMembers]);

  useEffect(() => {
    fetchMembers();
  }, [fetchMembers]);

  return {
    members,
    loading,
    error,
    refresh: fetchMembers,
    addMember,
    updateMember,
    removeMember,
    defaultColors: DEFAULT_MEMBER_COLORS,
    defaultEmojis: DEFAULT_MEMBER_EMOJIS,
  };
}

export function useMemberTransactions(memberId: number | null, year: number, month: number) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { getTransactionsByMember } = useIPC();

  const fetchTransactions = useCallback(async () => {
    if (!memberId) {
      setTransactions([]);
      return;
    }

    try {
      setLoading(true);
      const results = await getTransactionsByMember(memberId, year, month);
      setTransactions(results);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  }, [getTransactionsByMember, memberId, year, month]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  return {
    transactions,
    loading,
    error,
    refresh: fetchTransactions,
  };
}

export function useMemberStats(year: number, month: number) {
  const [stats, setStats] = useState<MemberStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getMemberStats } = useIPC();

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      const results = await getMemberStats(year, month);
      setStats(results);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  }, [getMemberStats, year, month]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    loading,
    error,
    refresh: fetchStats,
  };
}

export function useSplitTransaction() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { assignTransactionMember, getTransactionMember } = useIPC();

  const assignToMember = useCallback(async (transactionId: number, memberId: number, splitAmount?: number) => {
    try {
      setLoading(true);
      await assignTransactionMember(transactionId, memberId, splitAmount ?? null);
      setError(null);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de l\'assignation');
      return false;
    } finally {
      setLoading(false);
    }
  }, [assignTransactionMember]);

  const getMemberForTransaction = useCallback(async (transactionId: number) => {
    try {
      const member = await getTransactionMember(transactionId);
      return member;
    } catch (err) {
      return null;
    }
  }, [getTransactionMember]);

  return {
    assignToMember,
    getMemberForTransaction,
    loading,
    error,
  };
}
