import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { format, startOfMonth, endOfMonth } from "date-fns";
import { useAuth } from "@/hooks/useAuth";

export interface MemberBalance {
  userId: string;
  displayName: string;
  deposits: number;      // contributions to joint account
  spending: number;      // expenses on joint account
  categoryBreakdown: { name: string; color: string; amount: number }[];
}

export interface CoupleBalanceData {
  members: MemberBalance[];
  unattributed: { deposits: number; spending: number; count: number };
  contributionRatio: number; // partner A's target share (0-1)
  totalJointExpenses: number;
  totalJointDeposits: number;
  balanceDue: { fromName: string; toName: string; amount: number } | null;
  coupleExpenses: number; // shared expenses attributed to "Couple"
}

export function useCoupleBalance(month: Date) {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["couple-balance", format(month, "yyyy-MM")],
    enabled: !!user,
    queryFn: async () => {
      const start = format(startOfMonth(month), "yyyy-MM-dd");
      const end = format(endOfMonth(month), "yyyy-MM-dd");

      const { data: profile } = await supabase
        .from("profiles")
        .select("household_id, households(contribution_ratio)")
        .eq("id", user!.id)
        .single();

      const householdId = profile?.household_id;
      if (!householdId) throw new Error("No household");

      const contributionRatio = (profile.households as any)?.contribution_ratio ?? 0.5;

      // Get household members (unified table includes ghost members)
      const { data: members } = await supabase
        .from("household_members")
        .select("id, display_name, card_identifier, is_couple")
        .eq("household_id", householdId);

      // Get joint account transactions for the month
      const { data: txs, error } = await supabase
        .from("transactions")
        .select("amount, attributed_to, is_internal_transfer, category_id, categories(name, color, exclude_from_income), bank_accounts!inner(account_type)")
        .eq("bank_accounts.account_type", "joint")
        .gte("date", start)
        .lte("date", end);

      if (error) throw error;

      const memberMap = new Map<string, MemberBalance>();
      for (const m of members || []) {
        memberMap.set(m.id, {
          userId: m.id,
          displayName: m.display_name || "Membre",
          deposits: 0,
          spending: 0,
          categoryBreakdown: [],
        });
      }

      let unattributed = { deposits: 0, spending: 0, count: 0 };
      let totalJointExpenses = 0;
      let totalJointDeposits = 0;
      let coupleExpenses = 0; // Track expenses attributed to "Couple"
      const catMaps = new Map<string, Map<string, { name: string; color: string; amount: number }>>();
      
      // Find the couple member
      const coupleMember = members?.find(m => m.is_couple);

      for (const t of txs || []) {
        if (t.is_internal_transfer) continue;
        if ((t.categories as any)?.exclude_from_income) continue;

        const userId = t.attributed_to as string | null;
        const isExpense = t.amount < 0;
        const abs = Math.abs(t.amount);

        if (isExpense) {
          totalJointExpenses += abs;
          if (userId && memberMap.has(userId)) {
            // Check if this is attributed to the couple member
            if (coupleMember && userId === coupleMember.id) {
              coupleExpenses += abs;
              // Don't add couple expenses to individual member spending
            } else {
              memberMap.get(userId)!.spending += abs;
            }
            
            // Track category breakdown per member (including couple)
            if (!catMaps.has(userId)) catMaps.set(userId, new Map());
            const cat = t.categories as any;
            const catName = cat?.name || "Non catégorisé";
            const catColor = cat?.color || "#94a3b8";
            const cm = catMaps.get(userId)!;
            const entry = cm.get(catName) || { name: catName, color: catColor, amount: 0 };
            entry.amount += abs;
            cm.set(catName, entry);
          } else {
            unattributed.spending += abs;
            unattributed.count++;
          }
        } else {
          totalJointDeposits += abs;
          if (userId && memberMap.has(userId)) {
            memberMap.get(userId)!.deposits += abs;
          } else {
            unattributed.deposits += abs;
            unattributed.count++;
          }
        }
      }

      // Attach category breakdowns
      for (const [userId, cm] of catMaps) {
        if (memberMap.has(userId)) {
          memberMap.get(userId)!.categoryBreakdown = Array.from(cm.values()).sort((a, b) => b.amount - a.amount);
        }
      }

      // Filter out couple member from balance calculations  
      const membersArr = Array.from(memberMap.values()).filter(m => {
        const member = members?.find(member => member.id === m.userId);
        return !member?.is_couple;
      });

      // Calculate balance due based on contribution ratio
      // For couple expenses, split them according to contribution ratio
      let balanceDue: CoupleBalanceData["balanceDue"] = null;
      if (membersArr.length === 2 && (totalJointExpenses - coupleExpenses) > 0) {
        const [a, b] = membersArr;
        const aTargetShare = contributionRatio;
        const bTargetShare = 1 - contributionRatio;
        
        // Add couple expenses split to individual spending
        const aShareOfCouple = coupleExpenses * aTargetShare;
        const bShareOfCouple = coupleExpenses * bTargetShare;
        const aTotalSpending = a.spending + aShareOfCouple;
        const bTotalSpending = b.spending + bShareOfCouple;
        
        const aFairExpense = totalJointExpenses * aTargetShare;
        const bFairExpense = totalJointExpenses * bTargetShare;
        const aDiff = aTotalSpending - aFairExpense; // positive = overpaid
        const bDiff = bTotalSpending - bFairExpense;

        if (aDiff > 1) {
          balanceDue = { fromName: b.displayName, toName: a.displayName, amount: aDiff };
        } else if (bDiff > 1) {
          balanceDue = { fromName: a.displayName, toName: b.displayName, amount: bDiff };
        }
      }

      return {
        members: membersArr,
        unattributed,
        contributionRatio,
        totalJointExpenses,
        totalJointDeposits,
        balanceDue,
        coupleExpenses,
      } as CoupleBalanceData;
    },
  });
}
