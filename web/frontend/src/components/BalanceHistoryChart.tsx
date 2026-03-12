import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
import { Skeleton } from "@/components/ui/skeleton";
import { format, subMonths, startOfMonth, endOfMonth } from "date-fns";
import { fr } from "date-fns/locale";

const MEMBER_COLORS = ["hsl(217, 91%, 60%)", "hsl(280, 65%, 60%)"];

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + " €";
}

export function BalanceHistoryChart() {
  const { data, isLoading } = useQuery({
    queryKey: ["balance-history"],
    queryFn: async () => {
      const now = new Date();
      const start = format(startOfMonth(subMonths(now, 11)), "yyyy-MM-dd");
      const end = format(endOfMonth(now), "yyyy-MM-dd");

      const { data: profile } = await supabase
        .from("profiles")
        .select("household_id, households(contribution_ratio)")
        .eq("id", (await supabase.auth.getUser()).data.user!.id)
        .single();

      if (!profile?.household_id) return null;

      const { data: members } = await supabase
        .from("household_members")
        .select("id, display_name")
        .eq("household_id", profile.household_id);

      const { data: txs, error } = await supabase
        .from("transactions")
        .select("date, amount, attributed_to, is_internal_transfer, categories(exclude_from_income), bank_accounts!inner(account_type)")
        .eq("bank_accounts.account_type", "joint")
        .gte("date", start)
        .lte("date", end);

      if (error) throw error;

      const memberNames = new Map<string, string>();
      for (const m of members || []) memberNames.set(m.id, m.display_name);

      const months: any[] = [];
      for (let i = 11; i >= 0; i--) {
        const m = subMonths(now, i);
        const mStart = startOfMonth(m);
        const mEnd = endOfMonth(m);
        const label = format(m, "MMM yy", { locale: fr });

        const monthTxs = (txs || []).filter(t => {
          const d = new Date(t.date);
          return d >= mStart && d <= mEnd && !t.is_internal_transfer && !(t.categories as any)?.exclude_from_income;
        });

        const entry: any = { month: label };
        let hasData = false;

        for (const [memberId, name] of memberNames) {
          const spending = monthTxs
            .filter(t => t.attributed_to === memberId && t.amount < 0)
            .reduce((s, t) => s + Math.abs(t.amount), 0);
          const deposits = monthTxs
            .filter(t => t.attributed_to === memberId && t.amount > 0)
            .reduce((s, t) => s + t.amount, 0);
          entry[`${name}_dep`] = deposits;
          entry[`${name}_spend`] = spending;
          entry[`${name}_net`] = deposits - spending;
          if (spending > 0 || deposits > 0) hasData = true;
        }

        if (hasData) months.push(entry);
      }

      return { months, memberNames: Array.from(memberNames.values()) };
    },
  });

  if (isLoading) return <Skeleton className="h-[300px] w-full" />;
  if (!data?.months?.length || !data.memberNames.length) return null;

  const config = Object.fromEntries(
    data.memberNames.map((name, i) => [`${name}_net`, { label: `${name} (net)`, color: MEMBER_COLORS[i] }])
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Historique d'équilibre</CardTitle>
        <CardDescription>Solde net mensuel (dépôts − dépenses) sur le compte joint</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={config} className="h-[280px] w-full">
          <LineChart data={data.months}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border/50" />
            <XAxis dataKey="month" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
            <YAxis tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} tickFormatter={v => `${(v / 1000).toFixed(0)}k`} />
            <ChartTooltip content={<ChartTooltipContent formatter={(v) => fmt(Number(v))} />} />
            {data.memberNames.map((name, i) => (
              <Line
                key={name}
                type="monotone"
                dataKey={`${name}_net`}
                name={`${name} (net)`}
                stroke={MEMBER_COLORS[i]}
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            ))}
          </LineChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
