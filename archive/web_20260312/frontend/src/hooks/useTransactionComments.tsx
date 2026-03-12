import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";

export interface TransactionComment {
  id: string;
  transaction_id: string;
  user_id: string;
  display_name: string;
  content: string;
  created_at: string;
}

export function useTransactionComments(transactionId: string | null) {
  return useQuery({
    queryKey: ["transaction-comments", transactionId],
    enabled: !!transactionId,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("transaction_comments")
        .select("*")
        .eq("transaction_id", transactionId!)
        .order("created_at", { ascending: true });
      if (error) throw error;
      return data as TransactionComment[];
    },
  });
}

export function useAddTransactionComment() {
  const { user } = useAuth();
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async ({ transactionId, content, displayName }: {
      transactionId: string;
      content: string;
      displayName: string;
    }) => {
      if (!user) throw new Error("Non authentifié");
      const { error } = await supabase.from("transaction_comments").insert({
        transaction_id: transactionId,
        user_id: user.id,
        display_name: displayName,
        content: content.trim(),
      });
      if (error) throw error;
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ["transaction-comments", vars.transactionId] });
      qc.invalidateQueries({ queryKey: ["transaction-comment-counts"] });
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

/** Fetch comment counts for a list of transaction ids */
export function useTransactionCommentCounts(transactionIds: string[]) {
  return useQuery({
    queryKey: ["transaction-comment-counts", transactionIds],
    enabled: transactionIds.length > 0,
    queryFn: async () => {
      // Fetch all comments for these transactions, just id + transaction_id
      const { data, error } = await supabase
        .from("transaction_comments")
        .select("transaction_id")
        .in("transaction_id", transactionIds);
      if (error) throw error;
      const counts: Record<string, number> = {};
      for (const row of data || []) {
        counts[row.transaction_id] = (counts[row.transaction_id] || 0) + 1;
      }
      return counts;
    },
  });
}
