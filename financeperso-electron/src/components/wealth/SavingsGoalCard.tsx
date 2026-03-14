import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { SavingsGoal } from '@/types/wealth';

// Icons
const TargetIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
  </svg>
);

const CalendarIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/>
  </svg>
);

const PlusIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14"/><path d="M12 5v14"/>
  </svg>
);

// Format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount);
};

// Format date
const formatDate = (dateString?: string) => {
  if (!dateString) return 'Non définie';
  return new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date(dateString));
};

// Calculer le nombre de mois restants
const getMonthsRemaining = (deadline?: string): number | null => {
  if (!deadline) return null;
  const deadlineDate = new Date(deadline);
  const now = new Date();
  const months = (deadlineDate.getFullYear() - now.getFullYear()) * 12 + 
    (deadlineDate.getMonth() - now.getMonth());
  return Math.max(0, months);
};

interface SavingsGoalCardProps {
  goal: SavingsGoal;
  onContribute: (id: number) => void;
  onEdit: (goal: SavingsGoal) => void;
}

export function SavingsGoalCard({ goal, onContribute, onEdit }: SavingsGoalCardProps) {
  const percentage = Math.min(
    Math.round(((goal.current_amount || 0) / goal.target_amount) * 100),
    100
  );
  const remaining = goal.target_amount - (goal.current_amount || 0);
  const monthsRemaining = getMonthsRemaining(goal.deadline);
  const isCompleted = remaining <= 0;

  // Déterminer la couleur en fonction de la progression
  const getProgressColor = () => {
    if (isCompleted) return 'success';
    if (percentage >= 80) return 'success';
    if (percentage >= 50) return 'warning';
    return 'default';
  };

  return (
    <Card className="relative overflow-hidden hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${isCompleted ? 'bg-emerald-100 text-emerald-600' : 'bg-blue-100 text-blue-600'}`}>
              <TargetIcon />
            </div>
            <div>
              <CardTitle className="text-lg font-semibold">{goal.name}</CardTitle>
              {goal.category && (
                <Badge variant="secondary" className="mt-1">
                  {goal.category}
                </Badge>
              )}
            </div>
          </div>
          {isCompleted && (
            <Badge variant="success" className="bg-emerald-100 text-emerald-700">
              Atteint !
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Progress Bar */}
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-500">Progression</span>
            <span className="font-medium">{percentage}%</span>
          </div>
          <Progress 
            value={percentage} 
            size="lg"
            variant={getProgressColor() as any}
          />
        </div>

        {/* Amounts */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Actuel</p>
            <p className="text-lg font-semibold text-gray-900">
              {formatCurrency(goal.current_amount || 0)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Objectif</p>
            <p className="text-lg font-semibold text-gray-900">
              {formatCurrency(goal.target_amount)}
            </p>
          </div>
        </div>

        {/* Reste à économiser */}
        {!isCompleted && (
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Reste à économiser</span>
              <span className="font-semibold text-gray-900">{formatCurrency(remaining)}</span>
            </div>
          </div>
        )}

        {/* Deadline & Monthly Contribution */}
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2 text-gray-500">
            <CalendarIcon />
            <span>{formatDate(goal.deadline)}</span>
          </div>
          {monthsRemaining !== null && monthsRemaining > 0 && !isCompleted && (
            <span className="text-gray-500">
              {monthsRemaining} mois restants
            </span>
          )}
        </div>

        {/* Monthly contribution suggestion */}
        {!isCompleted && goal.monthly_contribution && goal.monthly_contribution > 0 && (
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
            <p className="text-sm text-blue-800">
              💡 Contribution mensuelle suggérée : <strong>{formatCurrency(goal.monthly_contribution)}</strong>
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={() => onEdit(goal)}
          >
            Modifier
          </Button>
          {!isCompleted && (
            <Button
              size="sm"
              className="flex-1"
              onClick={() => onContribute(goal.id)}
            >
              <PlusIcon />
              Contribuer
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
