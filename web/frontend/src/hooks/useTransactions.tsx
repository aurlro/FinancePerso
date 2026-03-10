/**
 * @file useTransactions.tsx
 * @description Hook pour la gestion des transactions - VERSION ADAPTÉE POUR FASTAPI
 * 
 * ⚠️  À ADAPTER : Remplacer les appels Supabase par des appels à l'API FastAPI
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

// TODO: Déplacer dans types/transaction.ts
export interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  type: "income" | "expense";
  category?: string;
  categoryId?: string;
  memberId?: string;
  accountId?: string;
  isRecurring?: boolean;
  notes?: string;
  status: "pending" | "validated" | "ignored";
  createdAt: string;
  updatedAt: string;
}

export interface CreateTransactionInput {
  date: string;
  description: string;
  amount: number;
  type: "income" | "expense";
  categoryId?: string;
  memberId?: string;
  accountId?: string;
  notes?: string;
}

export interface UpdateTransactionInput extends Partial<CreateTransactionInput> {
  id: string;
}

export interface TransactionFilters {
  startDate?: string;
  endDate?: string;
  categoryId?: string;
  memberId?: string;
  accountId?: string;
  type?: "income" | "expense";
  status?: "pending" | "validated" | "ignored";
  search?: string;
}

// ============================================
// MOCK DATA - À REMPLACER PAR API FASTAPI
// ============================================
const MOCK_TRANSACTIONS: Transaction[] = [
  {
    id: "tx-001",
    date: new Date().toISOString(),
    description: "Supermarché Casino",
    amount: -85.5,
    type: "expense",
    category: "Alimentation",
    status: "validated",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "tx-002",
    date: new Date(Date.now() - 86400000).toISOString(),
    description: "Salaire Mars",
    amount: 2500,
    type: "income",
    status: "validated",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "tx-003",
    date: new Date(Date.now() - 172800000).toISOString(),
    description: "Essence Total",
    amount: -65,
    type: "expense",
    category: "Transport",
    status: "pending",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

// ============================================
// API CLIENT
// ============================================
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem("fp_token");
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
}

// ============================================
// HOOKS
// ============================================

export function useTransactions(filters?: TransactionFilters) {
  return useQuery({
    queryKey: ["transactions", filters],
    queryFn: async (): Promise<Transaction[]> => {
      // TODO: Remplacer par : GET /api/transactions?startDate=...&endDate=...
      // const params = new URLSearchParams();
      // if (filters?.startDate) params.append("start_date", filters.startDate);
      // return fetchApi<Transaction[]>(`/transactions?${params}`);
      
      await new Promise(resolve => setTimeout(resolve, 300));
      return MOCK_TRANSACTIONS;
    },
  });
}

export function useTransaction(id: string) {
  return useQuery({
    queryKey: ["transactions", id],
    queryFn: async (): Promise<Transaction> => {
      // TODO: Remplacer par : GET /api/transactions/{id}
      await new Promise(resolve => setTimeout(resolve, 200));
      const tx = MOCK_TRANSACTIONS.find(t => t.id === id);
      if (!tx) throw new Error("Transaction not found");
      return tx;
    },
    enabled: !!id,
  });
}

export function useCreateTransaction() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (input: CreateTransactionInput): Promise<Transaction> => {
      // TODO: Remplacer par : POST /api/transactions
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const newTx: Transaction = {
        ...input,
        id: `tx-${Date.now()}`,
        status: "pending",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      return newTx;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useUpdateTransaction() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (input: UpdateTransactionInput): Promise<Transaction> => {
      // TODO: Remplacer par : PUT /api/transactions/{id}
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const tx = MOCK_TRANSACTIONS.find(t => t.id === input.id);
      if (!tx) throw new Error("Transaction not found");
      
      return { ...tx, ...input, updatedAt: new Date().toISOString() };
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["transactions", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDeleteTransaction() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      // TODO: Remplacer par : DELETE /api/transactions/{id}
      await new Promise(resolve => setTimeout(resolve, 300));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useImportTransactions() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (file: File): Promise<Transaction[]> => {
      // TODO: Remplacer par : POST /api/transactions/import (multipart/form-data)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log("[MOCK] Importing file:", file.name);
      return MOCK_TRANSACTIONS.slice(0, 2);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
