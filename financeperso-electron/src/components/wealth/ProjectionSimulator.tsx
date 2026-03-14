import * as React from 'react';
import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useProjections } from '@/hooks/useWealth';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine,
  Legend
} from 'recharts';

// Format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(amount);
};

// Format number
const formatNumber = (num: number) => {
  return new Intl.NumberFormat('fr-FR').format(num);
};

interface ProjectionSimulatorProps {
  initialInitialAmount?: number;
}

export function ProjectionSimulator({ initialInitialAmount = 0 }: ProjectionSimulatorProps) {
  const [initialAmount, setInitialAmount] = useState(initialInitialAmount);
  const [monthlyContribution, setMonthlyContribution] = useState(500);
  const [annualRate, setAnnualRate] = useState(5);
  const [years, setYears] = useState(10);

  const projections = useProjections({
    initialAmount,
    monthlyContribution,
    annualRate,
    years,
  });

  // Données pour le graphique (afficher par année)
  const chartData = useMemo(() => {
    return projections.monthlyData
      .filter((_, index) => (index + 1) % 12 === 0) // Un point par an
      .map(d => ({
        year: d.year,
        total: d.amount,
        contributions: d.contributions,
        interest: d.interest,
      }));
  }, [projections.monthlyData]);

  // Calculer le seuil d'indépendance financière (25x les dépenses annuelles estimées)
  // Estimation simple : contributions mensuelles * 12 * 25
  const financialIndependenceThreshold = useMemo(() => {
    return monthlyContribution * 12 * 25;
  }, [monthlyContribution]);

  // Année d'atteinte de l'indépendance financière
  const fiYear = useMemo(() => {
    const reached = projections.monthlyData.find(d => d.amount >= financialIndependenceThreshold);
    return reached?.year || null;
  }, [projections.monthlyData, financialIndependenceThreshold]);

  return (
    <div className="space-y-6">
      {/* Paramètres du simulateur */}
      <Card>
        <CardHeader>
          <CardTitle>Simulateur d'épargne</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Montant initial */}
            <div className="space-y-3">
              <div className="flex justify-between">
                <Label htmlFor="initial">Montant initial</Label>
                <span className="text-sm font-medium">{formatCurrency(initialAmount)}</span>
              </div>
              <Input
                id="initial"
                type="number"
                min="0"
                step="100"
                value={initialAmount}
                onChange={(e) => setInitialAmount(Number(e.target.value))}
              />
              <Slider
                value={[initialAmount]}
                onValueChange={([v]) => setInitialAmount(v)}
                max={100000}
                step={1000}
              />
            </div>

            {/* Contribution mensuelle */}
            <div className="space-y-3">
              <div className="flex justify-between">
                <Label htmlFor="monthly">Contribution mensuelle</Label>
                <span className="text-sm font-medium">{formatCurrency(monthlyContribution)}</span>
              </div>
              <Input
                id="monthly"
                type="number"
                min="0"
                step="10"
                value={monthlyContribution}
                onChange={(e) => setMonthlyContribution(Number(e.target.value))}
              />
              <Slider
                value={[monthlyContribution]}
                onValueChange={([v]) => setMonthlyContribution(v)}
                max={5000}
                step={50}
              />
            </div>

            {/* Taux d'intérêt */}
            <div className="space-y-3">
              <div className="flex justify-between">
                <Label htmlFor="rate">Taux annuel</Label>
                <span className="text-sm font-medium">{annualRate}%</span>
              </div>
              <Input
                id="rate"
                type="number"
                min="0"
                max="20"
                step="0.1"
                value={annualRate}
                onChange={(e) => setAnnualRate(Number(e.target.value))}
              />
              <Slider
                value={[annualRate]}
                onValueChange={([v]) => setAnnualRate(v)}
                max={15}
                step={0.5}
              />
            </div>

            {/* Durée */}
            <div className="space-y-3">
              <div className="flex justify-between">
                <Label htmlFor="years">Durée (années)</Label>
                <span className="text-sm font-medium">{years} ans</span>
              </div>
              <Input
                id="years"
                type="number"
                min="1"
                max="50"
                step="1"
                value={years}
                onChange={(e) => setYears(Number(e.target.value))}
              />
              <Slider
                value={[years]}
                onValueChange={([v]) => setYears(v)}
                min={1}
                max={40}
                step={1}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Résultats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-blue-50 border-blue-100">
          <CardContent className="p-4">
            <p className="text-sm text-blue-600 mb-1">Capital final estimé</p>
            <p className="text-3xl font-bold text-blue-900">
              {formatCurrency(projections.finalAmount)}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-emerald-50 border-emerald-100">
          <CardContent className="p-4">
            <p className="text-sm text-emerald-600 mb-1">Total des contributions</p>
            <p className="text-3xl font-bold text-emerald-900">
              {formatCurrency(projections.totalContributions)}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-violet-50 border-violet-100">
          <CardContent className="p-4">
            <p className="text-sm text-violet-600 mb-1">Intérêts gagnés</p>
            <p className="text-3xl font-bold text-violet-900">
              {formatCurrency(projections.totalInterest)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Graphique de projection */}
      <Card>
        <CardHeader>
          <CardTitle>Projection de croissance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorContributions" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis 
                  dataKey="year" 
                  tickFormatter={(year) => `${year}`}
                />
                <YAxis 
                  tickFormatter={(value) => `${(value / 1000).toFixed(0)}k€`}
                />
                <Tooltip
                  formatter={(value: number) => formatCurrency(value)}
                  labelFormatter={(label) => `Année ${label}`}
                />
                <Legend />
                <ReferenceLine 
                  y={financialIndependenceThreshold} 
                  stroke="#f59e0b" 
                  strokeDasharray="3 3"
                  label={{ value: "Indépendance FI", position: "right" }}
                />
                <Area
                  type="monotone"
                  dataKey="contributions"
                  name="Contributions"
                  stroke="#10b981"
                  fillOpacity={1}
                  fill="url(#colorContributions)"
                />
                <Area
                  type="monotone"
                  dataKey="total"
                  name="Capital total"
                  stroke="#3b82f6"
                  fillOpacity={1}
                  fill="url(#colorTotal)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          
          {fiYear && (
            <div className="mt-4 p-4 bg-amber-50 rounded-lg border border-amber-200">
              <p className="text-amber-800">
                🎯 <strong>Indépendance financière</strong> atteinte en <strong>{fiYear}</strong> 
                {' '}(seuil de {formatCurrency(financialIndependenceThreshold)})
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tableau récapitulatif */}
      <Card>
        <CardHeader>
          <CardTitle>Tableau d'évolution annuelle</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4 font-medium text-gray-500">Année</th>
                  <th className="text-right py-2 px-4 font-medium text-gray-500">Capital</th>
                  <th className="text-right py-2 px-4 font-medium text-gray-500">Contributions</th>
                  <th className="text-right py-2 px-4 font-medium text-gray-500">Intérêts</th>
                  <th className="text-right py-2 px-4 font-medium text-gray-500">Rendement</th>
                </tr>
              </thead>
              <tbody>
                {chartData.map((row, index) => (
                  <tr key={row.year} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="py-2 px-4 font-medium">{row.year}</td>
                    <td className="text-right py-2 px-4 font-semibold">{formatCurrency(row.total)}</td>
                    <td className="text-right py-2 px-4 text-emerald-600">{formatCurrency(row.contributions)}</td>
                    <td className="text-right py-2 px-4 text-violet-600">{formatCurrency(row.interest)}</td>
                    <td className="text-right py-2 px-4">
                      {row.contributions > 0 
                        ? `${((row.interest / row.contributions) * 100).toFixed(1)}%` 
                        : '0%'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
