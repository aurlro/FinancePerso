import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export interface BankAccount {
  id: string;
  name: string;
  bank_name?: string;
  account_type: "perso_a" | "perso_b" | "joint";
  balance: number;
  household_id: string;
  created_at: string;
}

// ============================================
// MOCK DATA - À remplacer par appels API
// ============================================
let MOCK_ACCOUNTS: BankAccount[] = [];

export function useAccounts() {
  return useQuery({
    queryKey: ["bank_accounts"],
    queryFn: async (): Promise<BankAccount[]> => {
      // TODO: GET /api/accounts
      return MOCK_ACCOUNTS;
    },
  });
}

export function useCreateAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (account: Omit<BankAccount, "id" | "created_at">) => {
      const newAccount: BankAccount = {
        ...account,
        id: `acc-${Date.now()}`,
        created_at: new Date().toISOString(),
      };
      MOCK_ACCOUNTS.push(newAccount);
      return newAccount;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["bank_accounts"] });
      toast.success("Compte ajouté");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useUpdateAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...updates }: Partial<BankAccount> & { id: string }) => {
      const idx = MOCK_ACCOUNTS.findIndex(a => a.id === id);
      if (idx >= 0) {
        MOCK_ACCOUNTS[idx] = { ...MOCK_ACCOUNTS[idx], ...updates };
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["bank_accounts"] });
      toast.success("Compte mis à jour");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useDeleteAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      MOCK_ACCOUNTS = MOCK_ACCOUNTS.filter(a => a.id !== id);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["bank_accounts"] });
      toast.success("Compte supprimé");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useHouseholdId() {
  return "household-1";
}
