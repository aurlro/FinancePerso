import { useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAccounts } from "@/hooks/useAccounts";
import { useCategories } from "@/hooks/useCategories";
import { Search, ArrowUpDown } from "lucide-react";

export default function Transactions() {
  const [search, setSearch] = useState("");
  const [accountFilter, setAccountFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");

  const { data: accounts } = useAccounts();
  const { data: categories } = useCategories();

  const { data: transactions, isLoading } = useQuery({
    queryKey: ["transactions"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("transactions")
        .select("*, bank_accounts(name, account_type), categories(name, color)")
        .order("date", { ascending: false })
        .limit(500);
      if (error) throw error;
      return data;
    },
  });

  const filtered = transactions?.filter(t => {
    if (search && !t.label.toLowerCase().includes(search.toLowerCase())) return false;
    if (accountFilter !== "all" && t.bank_account_id !== accountFilter) return false;
    if (categoryFilter !== "all" && t.category_id !== categoryFilter) return false;
    return true;
  });

  return (
    <AppLayout title="Transactions">
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Rechercher…" className="pl-9" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <Select value={accountFilter} onValueChange={setAccountFilter}>
          <SelectTrigger className="w-[200px]"><SelectValue placeholder="Tous les comptes" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les comptes</SelectItem>
            {accounts?.map(a => <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-[200px]"><SelectValue placeholder="Toutes catégories" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Toutes catégories</SelectItem>
            {categories?.map(c => <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-3">
              {[1, 2, 3, 4, 5].map(i => <Skeleton key={i} className="h-10 w-full" />)}
            </div>
          ) : !filtered?.length ? (
            <div className="flex flex-col items-center justify-center py-16">
              <ArrowUpDown className="h-10 w-10 text-muted-foreground/50 mb-4" />
              <h3 className="text-lg font-medium">Aucune transaction</h3>
              <p className="text-sm text-muted-foreground mt-1">Importez un relevé CSV pour commencer.</p>
            </div>
          ) : (
            <div className="overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Libellé</TableHead>
                    <TableHead>Compte</TableHead>
                    <TableHead>Catégorie</TableHead>
                    <TableHead className="text-right">Montant</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filtered.map(t => (
                    <TableRow key={t.id}>
                      <TableCell className="whitespace-nowrap text-sm">{new Date(t.date).toLocaleDateString("fr-FR")}</TableCell>
                      <TableCell className="max-w-[300px] truncate text-sm">{t.label}</TableCell>
                      <TableCell>
                        {t.bank_accounts && (
                          <Badge variant="outline" className="text-xs">{(t.bank_accounts as any).name}</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {t.categories ? (
                          <Badge variant="secondary" className="text-xs">{(t.categories as any).name}</Badge>
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell className={`text-right font-mono text-sm whitespace-nowrap ${t.amount < 0 ? "text-destructive" : "text-emerald-600 dark:text-emerald-400"}`}>
                        {t.amount > 0 ? "+" : ""}{Number(t.amount).toFixed(2)} €
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </AppLayout>
  );
}
