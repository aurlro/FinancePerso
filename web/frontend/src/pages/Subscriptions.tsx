import { useMemo } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { subMonths, format, startOfMonth, endOfMonth } from "date-fns";
import { fr } from "date-fns/locale";
import { RefreshCw, AlertTriangle, TrendingDown } from "lucide-react";

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
}

interface RecurringTransaction {
  label: string;
  avgAmount: number;
  frequency: number; // months seen out of last 6
  lastDate: string;
  categoryName: string | null;
  categoryColor: string | null;
  months: string[];
  isManual: boolean; // manually flagged via is_subscription
}

export default function Subscriptions() {
  const { data: txs, isLoading } = useQuery({
    queryKey: ["subscriptions-analysis"],
    queryFn: async () => {
      const now = new Date();
      const start = format(startOfMonth(subMonths(now, 5)), "yyyy-MM-dd");
      const end = format(endOfMonth(now), "yyyy-MM-dd");

      const { data, error } = await supabase
        .from("transactions")
        .select("label, amount, date, is_internal_transfer, is_subscription, categories(name, color)")
        .gte("date", start)
        .lte("date", end)
        .lt("amount", 0)
        .eq("is_internal_transfer", false)
        .order("date", { ascending: false });

      if (error) throw error;
      return data;
    },
  });

  const recurring = useMemo(() => {
    if (!txs?.length) return [];

    // Normalize labels: lowercase, trim, remove trailing numbers/dates
    const normalize = (label: string) => 
      label.toLowerCase().replace(/\d{2}\/\d{2}(\/\d{2,4})?/g, "").replace(/\s+/g, " ").trim();

    const groups = new Map<string, { labels: string[]; amounts: number[]; dates: string[]; cat: any; hasManual: boolean }>();

    for (const t of txs) {
      const key = normalize(t.label);
      if (!key || key.length < 4) continue;
      const g = groups.get(key) || { labels: [], amounts: [], dates: [], cat: null, hasManual: false };
      g.labels.push(t.label);
      g.amounts.push(Math.abs(t.amount));
      g.dates.push(t.date);
      if (t.categories) g.cat = t.categories;
      if ((t as any).is_subscription) g.hasManual = true;
      groups.set(key, g);
    }

    const results: RecurringTransaction[] = [];

    for (const [, g] of groups) {
      const monthSet = new Set(g.dates.map(d => d.substring(0, 7)));
      const mean = g.amounts.reduce((a, b) => a + b, 0) / g.amounts.length;

      // Auto-detected: at least 3 months + consistent amount
      const variance = g.amounts.reduce((s, v) => s + (v - mean) ** 2, 0) / g.amounts.length;
      const stdDev = Math.sqrt(variance);
      const isAutoDetected = monthSet.size >= 3 && (mean === 0 || stdDev / mean <= 0.3);

      // Include if auto-detected OR manually flagged
      if (!isAutoDetected && !g.hasManual) continue;

      results.push({
        label: g.labels[0],
        avgAmount: mean,
        frequency: monthSet.size,
        lastDate: g.dates[0],
        categoryName: (g.cat as any)?.name || null,
        categoryColor: (g.cat as any)?.color || null,
        months: Array.from(monthSet).sort(),
        isManual: g.hasManual && !isAutoDetected,
      });
    }

    return results.sort((a, b) => b.avgAmount - a.avgAmount);
  }, [txs]);

  const totalMonthly = recurring.reduce((s, r) => s + r.avgAmount, 0);

  return (
    <AppLayout title="Abonnements & Récurrences">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Abonnements détectés</h2>
          <p className="text-muted-foreground">Transactions récurrentes identifiées sur les 6 derniers mois</p>
        </div>

        {/* KPI */}
        <div className="grid gap-4 sm:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <RefreshCw className="h-4 w-4" /> Abonnements détectés
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? <Skeleton className="h-8 w-16" /> : (
                <p className="text-2xl font-bold">{recurring.length}</p>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <TrendingDown className="h-4 w-4" /> Coût mensuel estimé
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? <Skeleton className="h-8 w-24" /> : (
                <p className="text-2xl font-bold text-destructive">{fmt(totalMonthly)}</p>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <TrendingDown className="h-4 w-4" /> Coût annuel estimé
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? <Skeleton className="h-8 w-24" /> : (
                <p className="text-2xl font-bold text-destructive">{fmt(totalMonthly * 12)}</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Table */}
        <Card>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-6 space-y-3">
                {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-10 w-full" />)}
              </div>
            ) : !recurring.length ? (
              <div className="flex flex-col items-center justify-center py-16">
                <RefreshCw className="h-10 w-10 text-muted-foreground/50 mb-4" />
                <h3 className="text-lg font-medium">Aucun abonnement détecté</h3>
                <p className="text-sm text-muted-foreground mt-1">Les transactions récurrentes apparaîtront ici après quelques mois de données.</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Libellé</TableHead>
                    <TableHead>Catégorie</TableHead>
                    <TableHead>Fréquence</TableHead>
                    <TableHead>Dernier prélèvement</TableHead>
                    <TableHead className="text-right">Montant moyen</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recurring.map((r, i) => (
                    <TableRow key={i}>
                      <TableCell className="max-w-[300px]">
                        <span className="text-sm truncate block">{r.label}</span>
                      </TableCell>
                      <TableCell>
                        {r.categoryName ? (
                          <Badge variant="secondary" className="text-xs gap-1">
                            {r.categoryColor && <span className="h-2 w-2 rounded-full" style={{ backgroundColor: r.categoryColor }} />}
                            {r.categoryName}
                          </Badge>
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant={r.frequency >= 5 ? "default" : "outline"} className="text-xs">
                          {r.isManual ? "Manuel" : `${r.frequency}/6 mois`}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm">
                        {new Date(r.lastDate).toLocaleDateString("fr-FR")}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm text-destructive">
                        -{fmt(r.avgAmount)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
