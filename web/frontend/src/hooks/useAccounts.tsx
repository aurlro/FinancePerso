/**
 * @file useAccounts.tsx
 * @description Hook pour la gestion des comptes bancaires - VERSION API FASTAPI
 * 
 * Endpoints utilisés:
 * - GET /api/accounts
 * - POST /api/accounts
 * - PUT /api/accounts/:id
 * - DELETE /api/accounts/:id
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { accountsApi, type Account, type CreateAccountInput, type UpdateAccountInput } from "@/lib/api";

export interface BankAccount {
  id: string;
  name: string;
  bank_name?: string;
  account_type: "perso_a" | "perso_b" | "joint";
  balance: number;
  household_id?: number;
  created_at: string;
  updated_at?: string;
}

// Convert API Account to hook's BankAccount format
function mapApiAccountToBankAccount(account: Account): BankAccount {
  return {
    id: account.id.toString(),
    name: account.name,
    bank_name: account.bank_name,
    account_type: account.account_type,
    balance: account.balance,
    household_id: account.household_id,
    created_at: account.created_at,
    updated_at: account.updated_at,
  };
}

// ============================================
// HOOKS
// ============================================

export function useAccounts() {
  return useQuery({
    queryKey: ["accounts"],
    queryFn: async (): Promise<BankAccount[]> => {
      const response = await accountsApi.list();
      return response.items.map(mapApiAccountToBankAccount);
    },
    staleTime: 30000, // 30 seconds
  });
}

export function useCreateAccount() {
  const qc = useQueryClient();
  
  return useMutation({
    mutationFn: async (account: Omit<BankAccount, "id" | "created_at">): Promise<BankAccount> => {
      const newAccount = await accountsApi.create({
        name: account.name,
        bank_name: account.bank_name,
        account_type: account.account_type,
        balance: account.balance,
      });
      return mapApiAccountToBankAccount(newAccount);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      toast.success("Compte ajouté");
    },
    onError: (e: Error) => {
      toast.error(e.message || "Erreur lors de la création du compte");
    },
  });
}

export function useUpdateAccount() {
  const qc = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, ...updates }: { id: string } & Partial<CreateAccountInput>): Promise<BankAccount> => {
      const updatedAccount = await accountsApi.update(parseInt(id), updates);
      return mapApiAccountToBankAccount(updatedAccount);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      toast.success("Compte mis à jour");
    },
    onError: (e: Error) => {
      toast.error(e.message || "Erreur lors de la mise à jour");
    },
  });
}

export function useDeleteAccount() {
  const qc = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      await accountsApi.delete(parseInt(id));
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      toast.success("Compte supprimé");
    },
    onError: (e: Error) => {
      toast.error(e.message || "Erreur lors de la suppression");
    },
  });
}

// Legacy compatibility - returns a fixed household ID for now
// TODO: Implement proper household management
export function useHouseholdId() {
  return "household-1";
}
