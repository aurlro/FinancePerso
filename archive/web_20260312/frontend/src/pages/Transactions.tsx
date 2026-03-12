import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Toggle } from "@/components/ui/toggle";
import { Checkbox } from "@/components/ui/checkbox";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAccounts } from "@/hooks/useAccounts";
import { useCategories } from "@/hooks/useCategories";
import { useHouseholdMembers, useUpdateMemberCard } from "@/hooks/useHousehold";
import { useHousehold } from "@/hooks/useHousehold";
import { useTransactionCommentCounts } from "@/hooks/useTransactionComments";
import { extractCardIdentifier } from "@/lib/card-identifier";
import { InlineCategoryPicker } from "@/components/InlineCategoryPicker";
import { InlineMemberPicker } from "@/components/InlineMemberPicker";
import { TransactionComments } from "@/components/TransactionComments";
import { Search, ArrowUpDown, Sparkles, Loader2, ChevronLeft, ChevronRight, ArrowLeftRight, X, UserCheck, MessageSquare, ShieldCheck, ShieldQuestion, ShieldX, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { format, startOfMonth, endOfMonth, parse } from "date-fns";
import { maybeCreateAutoRule, maybeCreateAutoAttributionRule } from "@/lib/auto-rule-generator";
import { useAuth } from "@/hooks/useAuth";
import { fr } from "date-fns/locale";
import { createNotification } from "@/hooks/useNotifications";

const PAGE_SIZE = 50;

function generateMonthOptions() {
  const options: { value: string; label: string }[] = [];
  const now = new Date();
  for (let i = 0; i < 24; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    options.push({ value: format(d, "yyyy-MM"), label: format(d, "MMMM yyyy", { locale: fr }) });
  }
  return options;
}

export default function Transactions() {
  const { user } = useAuth();
  const { data: profile } = useHousehold();
  const [searchParams, setSearchParams] = useSearchParams();
  const [search, setSearch] = useState("");
  const [accountFilter, setAccountFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [monthFilter, setMonthFilter] = useState("all");
  const [validationFilter, setValidationFilter] = useState("all");
  const [hideTransfers, setHideTransfers] = useState(false);
  const [subscriptionFilter, setSubscriptionFilter] = useState(false);
  const [page, setPage] = useState(0);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [commentTx, setCommentTx] = useState<{ id: string; label: string } | null>(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    const cat = searchParams.get("category");
    const month = searchParams.get("month");
    if (cat) setCategoryFilter(cat);
    if (month) setMonthFilter(month);
    if (cat || month) setSearchParams({}, { replace: true });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const monthOptions = generateMonthOptions();

  const { data: accounts } = useAccounts();
  const { data: categories } = useCategories();
  const { data: householdMembers } = useHouseholdMembers();
  const updateMemberCard = useUpdateMemberCard();

  const maybeProposeCardLink = (label: string, memberId: string | null) => {
    if (!memberId || !householdMembers) return;
    const cardId = extractCardIdentifier(label);
    if (!cardId) return;
    const member = householdMembers.find(m => m.id === memberId);
    if (!member || member.card_identifier) return;
    toast(`Associer la carte ${cardId} à ${member.display_name} ?`, {
      action: { label: "Associer", onClick: () => updateMemberCard.mutate({ id: memberId, cardIdentifier: cardId }) },
      duration: 8000,
    });
  };

  const { data: result, isLoading } = useQuery({
    queryKey: ["transactions", page, search, accountFilter, categoryFilter, monthFilter, hideTransfers, validationFilter, subscriptionFilter],
    queryFn: async () => {
      let countQuery = supabase.from("transactions").select("id", { count: "exact", head: true });
      let query = supabase
        .from("transactions")
        .select("*, bank_accounts(name, account_type), categories(name, color), household_members(display_name, is_active, is_couple)")
        .order("date", { ascending: false })
        .range(page * PAGE_SIZE, (page + 1) * PAGE_SIZE - 1);

      if (search) {
        const s = search.trim().slice(0, 100);
        query = query.ilike("label", `%${s}%`);
        countQuery = countQuery.ilike("label", `%${s}%`);
      }
      if (accountFilter !== "all") { query = query.eq("bank_account_id", accountFilter); countQuery = countQuery.eq("bank_account_id", accountFilter); }
      if (categoryFilter === "uncategorized") { query = query.is("category_id", null); countQuery = countQuery.is("category_id", null); }
      else if (categoryFilter !== "all") { query = query.eq("category_id", categoryFilter); countQuery = countQuery.eq("category_id", categoryFilter); }
      if (subscriptionFilter) { query = query.eq("is_subscription", true); countQuery = countQuery.eq("is_subscription", true); }
      if (monthFilter !== "all") {
        const monthDate = parse(monthFilter, "yyyy-MM", new Date());
        const mStart = format(startOfMonth(monthDate), "yyyy-MM-dd");
        const mEnd = format(endOfMonth(monthDate), "yyyy-MM-dd");
        query = query.gte("date", mStart).lte("date", mEnd);
        countQuery = countQuery.gte("date", mStart).lte("date", mEnd);
      }
      if (hideTransfers) { query = query.eq("is_internal_transfer", false); countQuery = countQuery.eq("is_internal_transfer", false); }
      if (validationFilter === "pending") { query = query.eq("validation_status", "pending"); countQuery = countQuery.eq("validation_status", "pending"); }

      const [{ data, error }, { count, error: countError }] = await Promise.all([query, countQuery]);
      if (error) throw error;
      if (countError) throw countError;
      return { transactions: data || [], totalCount: count || 0 };
    },
  });

  const transactions = result?.transactions;
  const totalCount = result?.totalCount || 0;
  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  // Comment counts
  const txIds = transactions?.map(t => t.id) || [];
  const { data: commentCounts } = useTransactionCommentCounts(txIds);

  const handleSearch = (v: string) => { setSearch(v); setPage(0); };
  const handleAccountFilter = (v: string) => { setAccountFilter(v); setPage(0); };
  const handleCategoryFilter = (v: string) => { setCategoryFilter(v); setPage(0); };
  const handleMonthFilter = (v: string) => { setMonthFilter(v); setPage(0); };
  const hasActiveFilters = categoryFilter !== "all" || monthFilter !== "all" || accountFilter !== "all" || search || hideTransfers || validationFilter !== "all" || subscriptionFilter;
  const clearAllFilters = () => { setCategoryFilter("all"); setMonthFilter("all"); setAccountFilter("all"); setSearch(""); setHideTransfers(false); setValidationFilter("all"); setSubscriptionFilter(false); setPage(0); };

  // --- Mutations ---

  const updateCategoryMutation = useMutation({
    mutationFn: async ({ transactionId, categoryId, label }: { transactionId: string; categoryId: string | null; label: string }) => {
      const { error } = await supabase.from("transactions").update({ category_id: categoryId, validation_status: "pending", last_modified_by: user?.id ?? null }).eq("id", transactionId);
      if (error) throw error;
      return { categoryId, label };
    },
    onSuccess: async ({ categoryId, label }) => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      if (categoryId && user) {
        try {
          const { data: p } = await supabase.from("profiles").select("household_id").eq("id", user.id).single();
          if (p?.household_id) {
            const created = await maybeCreateAutoRule({ label, categoryId, householdId: p.household_id });
            if (created) toast.success("Règle créée automatiquement", { duration: 2000 });
            // Notify partner
            notifyPartner(p.household_id, "attribution_change", "Catégorie modifiée", `${label.slice(0, 50)} — catégorie mise à jour`);
          }
        } catch { /* silent */ }
      }
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const updateAttributionMutation = useMutation({
    mutationFn: async ({ transactionId, memberId, label }: { transactionId: string; memberId: string | null; label: string }) => {
      const { error } = await supabase.from("transactions").update({ attributed_to: memberId, validation_status: "pending", last_modified_by: user?.id ?? null }).eq("id", transactionId);
      if (error) throw error;
      return { memberId, label };
    },
    onSuccess: async ({ memberId, label }) => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      maybeProposeCardLink(label, memberId);
      if (memberId && user) {
        try {
          const { data: p } = await supabase.from("profiles").select("household_id").eq("id", user.id).single();
          if (p?.household_id) {
            const created = await maybeCreateAutoAttributionRule({ label, memberId, householdId: p.household_id });
            if (created) toast.success("Règle d'attribution créée automatiquement", { duration: 2000 });
            notifyPartner(p.household_id, "attribution_change", "Attribution modifiée", `${label.slice(0, 50)} — membre mis à jour`);
          }
        } catch { /* silent */ }
      }
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const validationMutation = useMutation({
    mutationFn: async ({ transactionId, status }: { transactionId: string; status: "validated" | "contested" }) => {
      const { error } = await supabase.from("transactions").update({ validation_status: status }).eq("id", transactionId);
      if (error) throw error;
      return status;
    },
    onSuccess: (status) => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      toast.success(status === "validated" ? "Transaction validée" : "Transaction contestée");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const bulkValidateMutation = useMutation({
    mutationFn: async (txIds: string[]) => {
      const { error } = await supabase.from("transactions").update({ validation_status: "validated" }).in("id", txIds);
      if (error) throw error;
      return txIds.length;
    },
    onSuccess: (count) => { toast.success(`${count} transaction${count > 1 ? "s" : ""} validée${count > 1 ? "s" : ""}`); setSelectedIds(new Set()); queryClient.invalidateQueries({ queryKey: ["transactions"] }); },
    onError: (e: Error) => toast.error(e.message),
  });

  const bulkSubscriptionMutation = useMutation({
    mutationFn: async ({ txIds, value }: { txIds: string[]; value: boolean }) => {
      const { error } = await supabase.from("transactions").update({ is_subscription: value } as any).in("id", txIds);
      if (error) throw error;
      return txIds.length;
    },
    onSuccess: (count) => { toast.success(`${count} transaction${count > 1 ? "s" : ""} ${count > 1 ? "marquées" : "marquée"} comme abonnement`); setSelectedIds(new Set()); queryClient.invalidateQueries({ queryKey: ["transactions"] }); },
    onError: (e: Error) => toast.error(e.message),
  });

  const notifyPartner = async (householdId: string, type: string, title: string, body: string) => {
    if (!user || !householdMembers) return;
    const partners = householdMembers.filter(m => m.user_id && m.user_id !== user.id);
    for (const p of partners) {
      createNotification({ householdId, userId: p.user_id!, type, title, body });
    }
  };

  const aiCategorizeMutation = useMutation({
    mutationFn: async () => {
      const { data: uncategorized, error: fetchErr } = await supabase.from("transactions").select("id, label, amount").is("category_id", null).limit(500);
      if (fetchErr) throw fetchErr;
      if (!uncategorized?.length) throw new Error("Toutes les transactions sont déjà catégorisées.");
      if (!categories?.length) throw new Error("Aucune catégorie disponible.");
      let totalUpdated = 0;
      const validCategoryIds = new Set(categories.map(c => c.id));
      for (let i = 0; i < uncategorized.length; i += 50) {
        const batch = uncategorized.slice(i, i + 50);
        const { data, error } = await supabase.functions.invoke("categorize-ai", {
          body: { transactions: batch.map(t => ({ id: t.id, label: t.label, amount: t.amount })), categories: categories.map(c => ({ id: c.id, name: c.name })) },
        });
        if (error) throw error;
        const suggestions: { transaction_id: string; category_id: string }[] = data?.suggestions || [];
        const byCat = new Map<string, string[]>();
        for (const s of suggestions) { if (!validCategoryIds.has(s.category_id)) continue; const list = byCat.get(s.category_id) || []; list.push(s.transaction_id); byCat.set(s.category_id, list); }
        for (const [catId, ids] of byCat) { const { error: e } = await supabase.from("transactions").update({ category_id: catId }).in("id", ids); if (!e) totalUpdated += ids.length; }
      }
      return totalUpdated;
    },
    onSuccess: (count) => { toast.success(`${count} transactions catégorisées par IA`); queryClient.invalidateQueries({ queryKey: ["transactions"] }); },
    onError: (e: Error) => toast.error(e.message),
  });

  const aiAttributeMutation = useMutation({
    mutationFn: async (txIds: string[]) => {
      if (!householdMembers?.length) throw new Error("Aucun membre du foyer.");
      const { data: txData, error: txErr } = await supabase.from("transactions").select("id, label, amount").in("id", txIds);
      if (txErr) throw txErr;
      if (!txData?.length) throw new Error("Aucune transaction trouvée.");
      const validMemberIds = new Set(householdMembers.map(m => m.id));
      let totalUpdated = 0;
      for (let i = 0; i < txData.length; i += 50) {
        const batch = txData.slice(i, i + 50);
        const { data, error } = await supabase.functions.invoke("attribute-ai", {
          body: { transactions: batch.map(t => ({ id: t.id, label: t.label, amount: t.amount })), members: householdMembers.map(m => ({ id: m.id, display_name: m.display_name, card_identifier: m.card_identifier })) },
        });
        if (error) throw error;
        const suggestions: { transaction_id: string; member_id: string | null }[] = data?.suggestions || [];
        const byMember = new Map<string, string[]>();
        for (const s of suggestions) { if (!s.member_id || !validMemberIds.has(s.member_id)) continue; const list = byMember.get(s.member_id) || []; list.push(s.transaction_id); byMember.set(s.member_id, list); }
        for (const [mId, ids] of byMember) { const { error: e } = await supabase.from("transactions").update({ attributed_to: mId }).in("id", ids); if (!e) totalUpdated += ids.length; }
      }
      return totalUpdated;
    },
    onSuccess: (count) => { toast.success(`${count} transaction${count > 1 ? "s" : ""} attribuée${count > 1 ? "s" : ""} par IA`); setSelectedIds(new Set()); queryClient.invalidateQueries({ queryKey: ["transactions"] }); },
    onError: (e: Error) => toast.error(e.message),
  });

  const bulkAttributeMutation = useMutation({
    mutationFn: async ({ txIds, memberId }: { txIds: string[]; memberId: string | null }) => {
      const { error } = await supabase.from("transactions").update({ attributed_to: memberId }).in("id", txIds);
      if (error) throw error;
      return txIds.length;
    },
    onSuccess: (count) => { toast.success(`${count} transaction${count > 1 ? "s" : ""} mise${count > 1 ? "s" : ""} à jour`); setSelectedIds(new Set()); queryClient.invalidateQueries({ queryKey: ["transactions"] }); },
    onError: (e: Error) => toast.error(e.message),
  });

  const toggleSubscriptionMutation = useMutation({
    mutationFn: async ({ txId, value }: { txId: string; value: boolean }) => {
      const { error } = await supabase.from("transactions").update({ is_subscription: value } as any).eq("id", txId);
      if (error) throw error;
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["transactions"] }); },
    onError: (e: Error) => toast.error(e.message),
  });

  const { data: uncategorizedCount = 0 } = useQuery({
    queryKey: ["transactions-uncategorized-count"],
    queryFn: async () => { const { count, error } = await supabase.from("transactions").select("id", { count: "exact", head: true }).is("category_id", null); if (error) throw error; return count || 0; },
  });

  const toggleSelect = (id: string) => { setSelectedIds(prev => { const next = new Set(prev); if (next.has(id)) next.delete(id); else next.add(id); return next; }); };
  const toggleSelectAll = () => { if (!transactions) return; if (selectedIds.size === transactions.length) setSelectedIds(new Set()); else setSelectedIds(new Set(transactions.map(t => t.id))); };
  const allSelected = transactions && transactions.length > 0 && selectedIds.size === transactions.length;

  const ValidationBadge = ({ status, txId, lastModifiedBy }: { status: string | null; txId: string; lastModifiedBy: string | null }) => {
    if (!status) return null;
    const canAct = true; // Anyone in the household can validate
    if (status === "validated") return (
      <Tooltip><TooltipTrigger><ShieldCheck className="h-3.5 w-3.5 text-emerald-500" /></TooltipTrigger>
        <TooltipContent>Validée</TooltipContent></Tooltip>
    );
    if (status === "contested") return (
      <Tooltip><TooltipTrigger><ShieldX className="h-3.5 w-3.5 text-destructive" /></TooltipTrigger>
        <TooltipContent>Contestée</TooltipContent></Tooltip>
    );
    // pending
    return (
      <div className="flex items-center gap-0.5">
        <Tooltip><TooltipTrigger><ShieldQuestion className="h-3.5 w-3.5 text-amber-500" /></TooltipTrigger>
          <TooltipContent>En attente de validation</TooltipContent></Tooltip>
        {canAct && (
          <>
            <Button variant="ghost" size="icon" className="h-5 w-5" onClick={() => validationMutation.mutate({ transactionId: txId, status: "validated" })}>
              <ShieldCheck className="h-3 w-3 text-emerald-500" />
            </Button>
            <Button variant="ghost" size="icon" className="h-5 w-5" onClick={() => { validationMutation.mutate({ transactionId: txId, status: "contested" }); setCommentTx({ id: txId, label: "" }); }}>
              <ShieldX className="h-3 w-3 text-destructive" />
            </Button>
          </>
        )}
      </div>
    );
  };

  return (
    <AppLayout title="Transactions">
      <div className="flex flex-col sm:flex-row gap-3 mb-4 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Rechercher…" className="pl-9" value={search} onChange={e => handleSearch(e.target.value)} />
        </div>
        <Select value={accountFilter} onValueChange={handleAccountFilter}>
          <SelectTrigger className={`w-[200px] ${accountFilter !== "all" ? "border-primary bg-primary/5" : ""}`}><SelectValue placeholder="Tous les comptes" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les comptes</SelectItem>
            {accounts?.map(a => <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={categoryFilter} onValueChange={handleCategoryFilter}>
          <SelectTrigger className={`w-[200px] ${categoryFilter !== "all" ? "border-primary bg-primary/5" : ""}`}><SelectValue placeholder="Toutes catégories" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Toutes catégories</SelectItem>
            <SelectItem value="uncategorized">Sans catégorie</SelectItem>
            {categories?.map(c => <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={monthFilter} onValueChange={handleMonthFilter}>
          <SelectTrigger className={`w-[200px] ${monthFilter !== "all" ? "border-primary bg-primary/5" : ""}`}><SelectValue placeholder="Toutes les périodes" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Toutes les périodes</SelectItem>
            {monthOptions.map(o => <SelectItem key={o.value} value={o.value} className="capitalize">{o.label}</SelectItem>)}
          </SelectContent>
        </Select>
        {hasActiveFilters && (
          <Button variant="ghost" size="sm" className="gap-1.5 text-xs text-muted-foreground" onClick={clearAllFilters}>
            <X className="h-3.5 w-3.5" /> Effacer filtres
          </Button>
        )}
        <Toggle variant="outline" size="sm" pressed={hideTransfers} onPressedChange={(v) => { setHideTransfers(v); setPage(0); }} className="gap-1.5 text-xs">
          <ArrowLeftRight className="h-3.5 w-3.5" />{hideTransfers ? "Virements masqués" : "Masquer virements"}
        </Toggle>
        <Toggle variant="outline" size="sm" pressed={validationFilter === "pending"} onPressedChange={(v) => { setValidationFilter(v ? "pending" : "all"); setPage(0); }} className="gap-1.5 text-xs">
          <ShieldQuestion className="h-3.5 w-3.5" />{validationFilter === "pending" ? "À valider" : "Validation"}
        </Toggle>
        <Toggle variant="outline" size="sm" pressed={subscriptionFilter} onPressedChange={(v) => { setSubscriptionFilter(v); setPage(0); }} className="gap-1.5 text-xs">
          <RefreshCw className="h-3.5 w-3.5" />{subscriptionFilter ? "Abonnements" : "Abonnements"}
        </Toggle>
        <Button
          variant={uncategorizedCount > 0 ? "default" : "outline"} size="sm" className="gap-2"
          onClick={() => aiCategorizeMutation.mutate()} disabled={aiCategorizeMutation.isPending || uncategorizedCount === 0}
        >
          {aiCategorizeMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          Catégoriser par IA {uncategorizedCount > 0 ? `(${uncategorizedCount})` : ""}
        </Button>
      </div>

      {(hasActiveFilters || totalCount > 0) && (
        <div className="flex flex-wrap items-center gap-2 mb-4">
          {totalCount > 0 && <span className="text-sm text-muted-foreground">{totalCount} transaction{totalCount > 1 ? "s" : ""}</span>}
          {accountFilter !== "all" && (
            <Badge variant="secondary" className="gap-1 cursor-pointer" onClick={() => handleAccountFilter("all")}>{accounts?.find(a => a.id === accountFilter)?.name}<X className="h-3 w-3" /></Badge>
          )}
          {categoryFilter === "uncategorized" && (
            <Badge variant="secondary" className="gap-1 cursor-pointer" onClick={() => handleCategoryFilter("all")}>Sans catégorie<X className="h-3 w-3" /></Badge>
          )}
          {categoryFilter !== "all" && categoryFilter !== "uncategorized" && (
            <Badge variant="secondary" className="gap-1 cursor-pointer" onClick={() => handleCategoryFilter("all")}>{categories?.find(c => c.id === categoryFilter)?.name}<X className="h-3 w-3" /></Badge>
          )}
          {monthFilter !== "all" && (
            <Badge variant="secondary" className="gap-1 cursor-pointer capitalize" onClick={() => handleMonthFilter("all")}>{monthOptions.find(o => o.value === monthFilter)?.label}<X className="h-3 w-3" /></Badge>
          )}
          {hideTransfers && (
            <Badge variant="secondary" className="gap-1 cursor-pointer" onClick={() => { setHideTransfers(false); setPage(0); }}>Virements masqués<X className="h-3 w-3" /></Badge>
          )}
          {validationFilter === "pending" && (
            <Badge variant="secondary" className="gap-1 cursor-pointer" onClick={() => { setValidationFilter("all"); setPage(0); }}>À valider<X className="h-3 w-3" /></Badge>
          )}
          {subscriptionFilter && (
            <Badge variant="secondary" className="gap-1 cursor-pointer" onClick={() => { setSubscriptionFilter(false); setPage(0); }}>Abonnements<X className="h-3 w-3" /></Badge>
          )}
          {search && (
            <Badge variant="secondary" className="gap-1 cursor-pointer" onClick={() => handleSearch("")}>« {search} »<X className="h-3 w-3" /></Badge>
          )}
        </div>
      )}

      {selectedIds.size > 0 && (
        <div className="flex items-center gap-3 mb-4 p-3 rounded-lg border bg-muted/50">
          <span className="text-sm font-medium">{selectedIds.size} sélectionnée{selectedIds.size > 1 ? "s" : ""}</span>
          <Button variant="default" size="sm" className="gap-1.5" onClick={() => aiAttributeMutation.mutate(Array.from(selectedIds))} disabled={aiAttributeMutation.isPending}>
            {aiAttributeMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}Attribuer par IA
          </Button>
          {householdMembers?.map(m => (
            <Button key={m.id} variant="outline" size="sm" className="gap-1.5 text-xs" onClick={() => bulkAttributeMutation.mutate({ txIds: Array.from(selectedIds), memberId: m.id })} disabled={bulkAttributeMutation.isPending}>
              <UserCheck className="h-3.5 w-3.5" />{m.display_name}
            </Button>
          ))}
          <Button variant="outline" size="sm" className="gap-1.5 text-xs" onClick={() => bulkValidateMutation.mutate(Array.from(selectedIds))} disabled={bulkValidateMutation.isPending}>
            {bulkValidateMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <ShieldCheck className="h-3.5 w-3.5" />}Tout valider
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5 text-xs" onClick={() => bulkSubscriptionMutation.mutate({ txIds: Array.from(selectedIds), value: true })} disabled={bulkSubscriptionMutation.isPending}>
            {bulkSubscriptionMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}Marquer abonnement
          </Button>
          <Button variant="ghost" size="sm" className="text-xs text-muted-foreground" onClick={() => setSelectedIds(new Set())}>Annuler</Button>
        </div>
      )}

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-3">{[1, 2, 3, 4, 5].map(i => <Skeleton key={i} className="h-10 w-full" />)}</div>
          ) : !transactions?.length ? (
            <div className="flex flex-col items-center justify-center py-16">
              <ArrowUpDown className="h-10 w-10 text-muted-foreground/50 mb-4" />
              <h3 className="text-lg font-medium">Aucune transaction</h3>
              <p className="text-sm text-muted-foreground mt-1">Importez un relevé CSV pour commencer.</p>
            </div>
          ) : (
            <>
              <div className="overflow-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-10"><Checkbox checked={allSelected} onCheckedChange={toggleSelectAll} /></TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Libellé</TableHead>
                      <TableHead>Compte</TableHead>
                      <TableHead>Catégorie</TableHead>
                      <TableHead>Attribué à</TableHead>
                      <TableHead className="text-right">Montant</TableHead>
                      <TableHead className="w-20"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {transactions.map(t => {
                      const cc = commentCounts?.[t.id] || 0;
                      return (
                        <TableRow key={t.id} className={`${t.is_internal_transfer ? "opacity-60" : ""} ${selectedIds.has(t.id) ? "bg-primary/5" : ""}`}>
                          <TableCell><Checkbox checked={selectedIds.has(t.id)} onCheckedChange={() => toggleSelect(t.id)} /></TableCell>
                          <TableCell className="whitespace-nowrap text-sm">{new Date(t.date).toLocaleDateString("fr-FR")}</TableCell>
                          <TableCell className="max-w-[300px] text-sm">
                            <div className="flex items-center gap-2">
                              <span className="truncate">{t.label}</span>
                              {(t as any).is_subscription && (
                                <Badge variant="outline" className="shrink-0 text-[10px] px-1.5 py-0 text-primary border-primary/30">
                                  <RefreshCw className="h-2.5 w-2.5 mr-0.5" />Abo
                                </Badge>
                              )}
                              {t.is_internal_transfer && (
                                <Badge variant="outline" className="shrink-0 text-[10px] px-1.5 py-0 text-blue-600 border-blue-300 dark:text-blue-400 dark:border-blue-600">
                                  <ArrowLeftRight className="h-2.5 w-2.5 mr-0.5" />Virement
                                </Badge>
                              )}
                              {!t.is_internal_transfer && (t.categories as any)?.name === "Contribution Partenaire" && (
                                <Badge variant="outline" className="shrink-0 text-[10px] px-1.5 py-0 text-purple-600 border-purple-300 dark:text-purple-400 dark:border-purple-600">Apport partenaire</Badge>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>{t.bank_accounts && <Badge variant="outline" className="text-xs">{(t.bank_accounts as any).name}</Badge>}</TableCell>
                          <TableCell>
                            {categories && (
                              <InlineCategoryPicker
                                categoryId={t.category_id} categoryName={(t.categories as any)?.name || null} categories={categories}
                                onSelect={(catId) => updateCategoryMutation.mutate({ transactionId: t.id, categoryId: catId, label: t.label })}
                                disabled={updateCategoryMutation.isPending}
                              />
                            )}
                          </TableCell>
                          <TableCell>
                            {householdMembers && (
                              <InlineMemberPicker
                                memberId={t.attributed_to} memberName={(t.household_members as any)?.display_name || null} members={householdMembers}
                                onSelect={(memberId) => updateAttributionMutation.mutate({ transactionId: t.id, memberId, label: t.label })}
                                disabled={updateAttributionMutation.isPending}
                              />
                            )}
                          </TableCell>
                          <TableCell className={`text-right font-mono text-sm whitespace-nowrap ${t.amount < 0 ? "text-destructive" : "text-emerald-600 dark:text-emerald-400"}`}>
                            {t.amount > 0 ? "+" : ""}{Number(t.amount).toFixed(2)} €
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-1">
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button variant="ghost" size="icon" className={`h-6 w-6 ${(t as any).is_subscription ? "text-primary" : "text-muted-foreground/40"}`}
                                    onClick={() => toggleSubscriptionMutation.mutate({ txId: t.id, value: !(t as any).is_subscription })}>
                                    <RefreshCw className="h-3.5 w-3.5" />
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>{(t as any).is_subscription ? "Retirer des abonnements" : "Marquer comme abonnement"}</TooltipContent>
                              </Tooltip>
                              <ValidationBadge status={(t as any).validation_status} txId={t.id} lastModifiedBy={(t as any).last_modified_by} />
                              <Button variant="ghost" size="icon" className="h-6 w-6 relative" onClick={() => setCommentTx({ id: t.id, label: t.label })}>
                                <MessageSquare className="h-3.5 w-3.5" />
                                {cc > 0 && <span className="absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-primary text-[9px] font-bold text-primary-foreground">{cc}</span>}
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>

              {totalPages > 1 && (
                <div className="flex items-center justify-between border-t px-4 py-3">
                  <p className="text-sm text-muted-foreground">{page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, totalCount)} sur {totalCount}</p>
                  <div className="flex items-center gap-1">
                    <Button variant="outline" size="icon" className="h-8 w-8" disabled={page === 0} onClick={() => setPage(p => p - 1)}><ChevronLeft className="h-4 w-4" /></Button>
                    {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                      let pageNum: number;
                      if (totalPages <= 7) pageNum = i;
                      else if (page < 4) pageNum = i;
                      else if (page > totalPages - 5) pageNum = totalPages - 7 + i;
                      else pageNum = page - 3 + i;
                      return <Button key={pageNum} variant={pageNum === page ? "default" : "outline"} size="icon" className="h-8 w-8 text-xs" onClick={() => setPage(pageNum)}>{pageNum + 1}</Button>;
                    })}
                    <Button variant="outline" size="icon" className="h-8 w-8" disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)}><ChevronRight className="h-4 w-4" /></Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      <TransactionComments
        transactionId={commentTx?.id ?? null}
        transactionLabel={commentTx?.label}
        open={!!commentTx}
        onOpenChange={(open) => { if (!open) setCommentTx(null); }}
      />
    </AppLayout>
  );
}
