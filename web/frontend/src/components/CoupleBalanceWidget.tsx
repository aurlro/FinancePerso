import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowRight, Users, ArrowRightLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { useCoupleBalance } from "@/hooks/useCoupleBalance";
import { Progress } from "@/components/ui/progress";

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + " €";
}

export function CoupleBalanceWidget({ month }: { month: Date }) {
  const { data, isLoading, isError } = useCoupleBalance(month);

  if (isLoading) return <Skeleton className="h-36 w-full" />;
  if (isError || !data || data.members.length < 2) return null;
  if (data.totalJointExpenses === 0 && data.totalJointDeposits === 0) return null;

  const [a, b] = data.members;
  const totalSpending = data.totalJointExpenses || 1;
  const totalDeposits = data.totalJointDeposits || 1;
  const personalSpending = data.totalJointExpenses - data.coupleExpenses;

  return (
    <Card className="border-accent/30 bg-accent/5">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-medium">Équilibre du couple</CardTitle>
          </div>
          <Button variant="ghost" size="sm" className="h-7 text-xs gap-1" asChild>
            <Link to="/balance">Détail <ArrowRight className="h-3 w-3" /></Link>
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Common expenses */}
        {data.coupleExpenses > 0 && (
          <div className="space-y-1.5">
            <p className="text-xs text-muted-foreground">Dépenses communes 👫</p>
            <div className="flex items-center gap-2 text-xs">
              <span className="w-20 truncate font-medium">Couple</span>
              <Progress value={(data.coupleExpenses / totalSpending) * 100} className="h-2 flex-1" />
              <span className="w-16 text-right font-mono text-muted-foreground">{fmt(data.coupleExpenses)}</span>
            </div>
          </div>
        )}

        {/* Personal spending split */}
        {personalSpending > 0 && (
          <div className="space-y-1.5">
            <p className="text-xs text-muted-foreground">Dépenses personnelles sur le compte joint</p>
            <div className="flex items-center gap-2 text-xs">
              <span className="w-20 truncate font-medium">{a.displayName}</span>
              <Progress value={(a.spending / personalSpending) * 100} className="h-2 flex-1" />
              <span className="w-16 text-right font-mono text-muted-foreground">{fmt(a.spending)}</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="w-20 truncate font-medium">{b.displayName}</span>
              <Progress value={(b.spending / personalSpending) * 100} className="h-2 flex-1" />
              <span className="w-16 text-right font-mono text-muted-foreground">{fmt(b.spending)}</span>
            </div>
          </div>
        )}

        {/* Contributions */}
        <div className="space-y-1.5">
          <p className="text-xs text-muted-foreground">Contributions au pot commun</p>
          <div className="flex items-center gap-2 text-xs">
            <span className="w-20 truncate font-medium">{a.displayName}</span>
            <Progress value={(a.deposits / totalDeposits) * 100} className="h-2 flex-1" />
            <span className="w-16 text-right font-mono text-muted-foreground">{fmt(a.deposits)}</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="w-20 truncate font-medium">{b.displayName}</span>
            <Progress value={(b.deposits / totalDeposits) * 100} className="h-2 flex-1" />
            <span className="w-16 text-right font-mono text-muted-foreground">{fmt(b.deposits)}</span>
          </div>
        </div>

        {/* Balance due */}
        {data.balanceDue && (
          <div className="flex items-center gap-2 rounded-md bg-muted/50 px-3 py-2 text-xs">
            <ArrowRightLeft className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
            <span>
              <strong className="font-medium">{data.balanceDue.fromName}</strong> doit <strong className="font-semibold text-primary">{fmt(data.balanceDue.amount)}</strong> à <strong className="font-medium">{data.balanceDue.toName}</strong>
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
