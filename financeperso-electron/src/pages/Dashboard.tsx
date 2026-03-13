import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { KPICard, ExpenseChart, TrendChart } from '@/components/charts';

import { useElectron } from '@/hooks/useElectron';
import { useMemberStats } from '@/hooks/useMembers';
import { cn } from '@/lib/utils';

function MemberMiniChart({ stats, totalExpense }: { stats: any[]; totalExpense: number }) {
  if (stats.length === 0 || totalExpense === 0) {
    return (
      <div className="text-center text-muted-foreground py-4 text-sm">
        Aucune dépense ce mois-ci
      </div>
    );
  }

  // Filtrer les membres avec des dépenses
  const activeStats = stats.filter(s => s.total > 0);
  
  if (activeStats.length === 0) {
    return (
      <div className="text-center text-muted-foreground py-4 text-sm">
        Aucune dépense assignée
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {activeStats.map((member) => {
        const percentage = totalExpense > 0 ? (member.total / totalExpense) * 100 : 0;
        return (
          <div key={member.id} className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-sm shrink-0"
              style={{ 
                backgroundColor: `${member.color}20`,
                border: `2px solid ${member.color}`
              }}
            >
              {member.emoji}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="font-medium truncate">{member.name}</span>
                <span className="text-muted-foreground">{percentage.toFixed(0)}%</span>
              </div>
              <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ 
                    width: `${Math.min(percentage, 100)}%`,
                    backgroundColor: member.color 
                  }}
                />
              </div>
            </div>
            <div className="text-sm font-bold shrink-0 w-16 text-right">
              {member.total.toFixed(0)}€
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function Dashboard() {
  const electron = useElectron();
  const [stats, setStats] = React.useState<any[]>([]);
  const [categories, setCategories] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);
  
  const { stats: memberStats, loading: memberStatsLoading } = useMemberStats(
    new Date().getFullYear(),
    new Date().getMonth() + 1
  );

  React.useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const now = new Date();
      const [statsData, catData] = await Promise.all([
        electron.getStatsByMonth(now.getFullYear(), now.getMonth() + 1),
        electron.getCategoriesStats(now.getFullYear(), now.getMonth() + 1),
      ]);
      setStats(statsData);
      setCategories(catData);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalIncome = stats.find(s => s.type === 'income')?.total || 0;
  const totalExpense = stats.find(s => s.type === 'expense')?.total || 0;
  const balance = totalIncome - totalExpense;
  
  const now = new Date();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500" />
        <span className="ml-3 text-muted-foreground">Chargement du tableau de bord...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Section KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KPICard
          title="Revenus du mois"
          value={totalIncome}
          variant="income"
          trend={5.2}
          trendLabel="vs mois dernier"
        />
        <KPICard
          title="Dépenses du mois"
          value={totalExpense}
          variant="expense"
          trend={-2.1}
          trendLabel="vs mois dernier"
        />
        <KPICard
          title="Solde"
          value={balance}
          variant="balance"
        />
      </div>

      {/* Section Graphiques */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TrendChart
          currentIncome={totalIncome}
          currentExpense={totalExpense}
          currentMonth={currentMonth}
          currentYear={currentYear}
        />
        <ExpenseChart data={categories} />
      </div>

      {/* Section Répartition par membre et par catégorie */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span>👥</span>
              Répartition par membre
            </CardTitle>
          </CardHeader>
          <CardContent>
            {memberStatsLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-500" />
              </div>
            ) : (
              <MemberMiniChart stats={memberStats} totalExpense={totalExpense} />
            )}
          </CardContent>
        </Card>

        <Card>
        <CardHeader>
          <CardTitle>Détail des dépenses par catégorie</CardTitle>
        </CardHeader>
        <CardContent>
          {categories.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              Aucune dépense ce mois-ci
            </p>
          ) : (
            <div className="space-y-3">
              {categories
                .sort((a, b) => b.total - a.total)
                .map((cat) => (
                  <div
                    key={cat.category}
                    className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
                  >
                    <span className="font-medium text-gray-900">{cat.category}</span>
                    <div className="flex items-center gap-4">
                      <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                          style={{
                            width: `${Math.min((cat.total / totalExpense) * 100, 100)}%`,
                          }}
                        />
                      </div>
                      <span className="font-bold w-24 text-right text-gray-900">
                        {cat.total.toFixed(2)}€
                      </span>
                      <span className="text-sm text-muted-foreground w-16 text-right">
                        {cat.count} tx
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          )}
        </CardContent>
        </Card>
      </div>
    </div>
  );
}
