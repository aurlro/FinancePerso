import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { transactionApi } from '@services/transactions';
import type { TransactionFilters, TransactionCreate, TransactionUpdate } from '@types';

const QUERY_KEY = 'transactions';

export const useTransactions = (filters?: TransactionFilters) => {
  return useQuery({
    queryKey: [QUERY_KEY, filters],
    queryFn: () => transactionApi.getAll(filters),
  });
};

export const useTransaction = (id: string) => {
  return useQuery({
    queryKey: [QUERY_KEY, id],
    queryFn: () => transactionApi.getById(id),
    enabled: !!id,
  });
};

export const useCreateTransaction = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TransactionCreate) => transactionApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      toast.success('Transaction créée avec succès');
    },
    onError: () => {
      toast.error('Erreur lors de la création de la transaction');
    },
  });
};

export const useUpdateTransaction = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TransactionUpdate }) =>
      transactionApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      toast.success('Transaction mise à jour');
    },
    onError: () => {
      toast.error('Erreur lors de la mise à jour');
    },
  });
};

export const useDeleteTransaction = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => transactionApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      toast.success('Transaction supprimée');
    },
    onError: () => {
      toast.error('Erreur lors de la suppression');
    },
  });
};

export const useValidateTransaction = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, categoryId }: { id: string; categoryId: string }) =>
      transactionApi.validate(id, categoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      toast.success('Transaction validée');
    },
  });
};
