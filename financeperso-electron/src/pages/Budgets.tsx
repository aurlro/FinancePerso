import * as React from 'react';
import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { useBudgets, useBudgetStatus } from '@/hooks/useBudgets';
import { useIPC } from '@/hooks/useIPC';
import type { Budget, BudgetStatus, Category } from '@/types';

// Icons
const PlusIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
    <path d="M5 12h14"/><path d="M12 5v14"/>
  </svg>
);

const EditIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
  </svg>
);

const TrashIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
  </svg>
);

const AlertTriangleIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/>
  </svg>
);

const ChevronLeftIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m15 18-6-6 6-6"/>
  </svg>
);

const ChevronRightIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m9 18 6-6-6-6"/>
  </svg>
);

// Format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount);
};

// Format month name
const formatMonthYear = (year: number, month: number) => {
  return new Intl.DateTimeFormat('fr-FR', { month: 'long', year: 'numeric' }).format(
    new Date(year, month - 1)
  );
};

// Budget Card Component
interface BudgetCardProps {
  budget: BudgetStatus;
  onEdit: (budget: BudgetStatus) => void;
  onDelete: (id: number) => void;
}

function BudgetCard({ budget, onEdit, onDelete }: BudgetCardProps) {
  const percentage = Math.min(budget.percentage, 100);
  const isExceeded = budget.spent_amount > budget.budget_amount;
  const isWarning = budget.percentage >= 80 && !isExceeded;

  return (
    <Card className="relative overflow-hidden">
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-semibold text-lg text-gray-900">{budget.category}</h3>
            <p className="text-sm text-gray-500">
              {budget.period === 'monthly' ? 'Budget mensuel' : 
               budget.period === 'yearly' ? 'Budget annuel' : 'Budget hebdomadaire'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {isExceeded && (
              <Badge variant="danger">Dépassé</Badge>
            )}
            {isWarning && (
              <Badge variant="warning">Attention</Badge>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit(budget)}
              className="h-8 w-8 p-0"
            >
              <EditIcon />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(budget.id)}
              className="h-8 w-8 p-0 text-red-500 hover:text-red-600 hover:bg-red-50"
            >
              <TrashIcon />
            </Button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <Progress 
            value={budget.spent_amount} 
            max={budget.budget_amount}
            size="lg"
            variant={isExceeded ? 'danger' : isWarning ? 'warning' : 'success'}
          />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Budget</p>
            <p className="font-semibold text-gray-900">{formatCurrency(budget.budget_amount)}</p>
          </div>
          <div>
            <p className="text-gray-500">Dépensé</p>
            <p className={`font-semibold ${isExceeded ? 'text-red-600' : 'text-gray-900'}`}>
              {formatCurrency(budget.spent_amount)}
            </p>
          </div>
          <div>
            <p className="text-gray-500">Reste</p>
            <p className={`font-semibold ${budget.remaining < 0 ? 'text-red-600' : 'text-emerald-600'}`}>
              {formatCurrency(budget.remaining)}
            </p>
          </div>
        </div>

        {/* Transactions count */}
        <p className="text-xs text-gray-400 mt-3">
          {budget.transaction_count} transaction{budget.transaction_count > 1 ? 's' : ''} cette période
        </p>
      </CardContent>
    </Card>
  );
}

// Budget Form Dialog
interface BudgetFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  budget?: BudgetStatus | null;
  categories: Category[];
  onSubmit: (data: Partial<Budget>) => void;
}

function BudgetFormDialog({ open, onOpenChange, budget, categories, onSubmit }: BudgetFormDialogProps) {
  const [formData, setFormData] = useState<Partial<Budget>>({
    category: '',
    amount: 0,
    period: 'monthly',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (budget) {
      setFormData({
        category: budget.category,
        amount: budget.budget_amount,
        period: budget.period,
        year: budget.year,
        month: budget.month,
      });
    } else {
      setFormData({
        category: '',
        amount: 0,
        period: 'monthly',
      });
    }
    setErrors({});
  }, [budget, open]);

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.category) {
      newErrors.category = 'Veuillez sélectionner une catégorie';
    }
    if (!formData.amount || formData.amount <= 0) {
      newErrors.amount = 'Le montant doit être supérieur à 0';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
      onOpenChange(false);
    }
  };

  // Filter out categories that already have budgets (for new budgets only)
  const availableCategories = budget 
    ? categories 
    : categories;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{budget ? 'Modifier le budget' : 'Nouveau budget'}</DialogTitle>
            <DialogDescription>
              {budget 
                ? 'Modifiez les détails de votre budget.' 
                : 'Définissez un budget pour une catégorie de dépenses.'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Category */}
            <div className="space-y-2">
              <Label htmlFor="category">Catégorie</Label>
              <Select
                id="category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                disabled={!!budget}
              >
                <option value="">Sélectionner une catégorie</option>
                {availableCategories.map((cat) => (
                  <option key={cat.name} value={cat.name}>
                    {cat.emoji} {cat.name}
                  </option>
                ))}
              </Select>
              {errors.category && (
                <p className="text-sm text-red-500">{errors.category}</p>
              )}
            </div>

            {/* Amount */}
            <div className="space-y-2">
              <Label htmlFor="amount">Montant du budget (€)</Label>
              <Input
                id="amount"
                type="number"
                min="0"
                step="0.01"
                value={formData.amount || ''}
                onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
                placeholder="0.00"
              />
              {errors.amount && (
                <p className="text-sm text-red-500">{errors.amount}</p>
              )}
            </div>

            {/* Period */}
            <div className="space-y-2">
              <Label htmlFor="period">Période</Label>
              <Select
                id="period"
                value={formData.period}
                onChange={(e) => setFormData({ ...formData, period: e.target.value as Budget['period'] })}
              >
                <option value="monthly">Mensuel</option>
                <option value="yearly">Annuel</option>
                <option value="weekly">Hebdomadaire</option>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Annuler
            </Button>
            <Button type="submit">
              {budget ? 'Mettre à jour' : 'Créer le budget'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// Delete Confirmation Dialog
interface DeleteDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  budgetName?: string;
}

function DeleteDialog({ open, onOpenChange, onConfirm, budgetName }: DeleteDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-red-600">
            <AlertTriangleIcon />
            Confirmer la suppression
          </DialogTitle>
          <DialogDescription>
            Êtes-vous sûr de vouloir supprimer le budget <strong>{budgetName}</strong> ?
            <br />
            Cette action est irréversible.
          </DialogDescription>
        </DialogHeader>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Annuler
          </Button>
          <Button type="button" variant="destructive" onClick={onConfirm}>
            Supprimer
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Main Budgets Page
export function Budgets() {
  const { getCategories } = useIPC();
  const { budgets, isLoading: budgetsLoading, error: budgetsError, addBudget, editBudget, removeBudget } = useBudgets();
  const [categories, setCategories] = useState<Category[]>([]);
  
  // Current month/year state
  const [currentDate, setCurrentDate] = useState(() => new Date());
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth() + 1;
  
  const { statuses, isLoading: statusLoading, refetch } = useBudgetStatus(year, month);
  
  // Dialog states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingBudget, setEditingBudget] = useState<BudgetStatus | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deletingBudgetId, setDeletingBudgetId] = useState<number | null>(null);
  const [deletingBudgetName, setDeletingBudgetName] = useState('');

  // Load categories
  useEffect(() => {
    getCategories().then(setCategories);
  }, [getCategories]);

  // Navigation handlers
  const goToPreviousMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() - 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() + 1));
  };

  const goToCurrentMonth = () => {
    setCurrentDate(new Date());
  };

  // Action handlers
  const handleAddClick = () => {
    setEditingBudget(null);
    setIsFormOpen(true);
  };

  const handleEditClick = (budget: BudgetStatus) => {
    setEditingBudget(budget);
    setIsFormOpen(true);
  };

  const handleDeleteClick = (id: number) => {
    const budget = statuses.find(b => b.id === id);
    setDeletingBudgetId(id);
    setDeletingBudgetName(budget?.category || '');
    setDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data: Partial<Budget>) => {
    try {
      if (editingBudget) {
        await editBudget(editingBudget.id, data);
      } else {
        await addBudget({ ...data, year, month });
      }
      refetch();
    } catch (err) {
      console.error('Error saving budget:', err);
    }
  };

  const handleDeleteConfirm = async () => {
    if (deletingBudgetId) {
      try {
        await removeBudget(deletingBudgetId);
        refetch();
        setDeleteDialogOpen(false);
      } catch (err) {
        console.error('Error deleting budget:', err);
      }
    }
  };

  // Calculate summary stats
  const totalBudget = statuses.reduce((sum, b) => sum + b.budget_amount, 0);
  const totalSpent = statuses.reduce((sum, b) => sum + b.spent_amount, 0);
  const totalRemaining = totalBudget - totalSpent;
  const exceededCount = statuses.filter(b => b.status === 'exceeded').length;
  const warningCount = statuses.filter(b => b.status === 'warning').length;

  const isLoading = budgetsLoading || statusLoading;
  const error = budgetsError;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Budgets</h1>
          <p className="text-gray-500 mt-1">Gérez vos budgets et suivez vos dépenses</p>
        </div>
        <Button onClick={handleAddClick}>
          <PlusIcon />
          Ajouter un budget
        </Button>
      </div>

      {/* Month Navigation */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <Button variant="ghost" onClick={goToPreviousMonth}>
              <ChevronLeftIcon />
            </Button>
            <div className="text-center">
              <h2 className="text-xl font-semibold capitalize">
                {formatMonthYear(year, month)}
              </h2>
              <Button 
                variant="link" 
                onClick={goToCurrentMonth}
                className="text-sm text-emerald-600"
              >
                Mois courant
              </Button>
            </div>
            <Button variant="ghost" onClick={goToNextMonth}>
              <ChevronRightIcon />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      {statuses.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500">Budget total</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalBudget)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500">Dépensé</p>
              <p className={`text-2xl font-bold ${totalSpent > totalBudget ? 'text-red-600' : 'text-gray-900'}`}>
                {formatCurrency(totalSpent)}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500">Reste</p>
              <p className={`text-2xl font-bold ${totalRemaining < 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                {formatCurrency(totalRemaining)}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500">Alertes</p>
              <div className="flex items-center gap-2">
                {exceededCount > 0 && (
                  <Badge variant="danger">{exceededCount} dépassé(s)</Badge>
                )}
                {warningCount > 0 && (
                  <Badge variant="warning">{warningCount} attention</Badge>
                )}
                {exceededCount === 0 && warningCount === 0 && (
                  <Badge variant="success">Tout va bien</Badge>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTitle>Erreur</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Empty State */}
      {!isLoading && statuses.length === 0 && !error && (
        <Card className="py-12">
          <CardContent className="text-center">
            <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl">💰</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Aucun budget défini
            </h3>
            <p className="text-gray-500 mb-4 max-w-md mx-auto">
              Commencez par créer un budget pour suivre vos dépenses par catégorie.
            </p>
            <Button onClick={handleAddClick}>
              <PlusIcon />
              Créer mon premier budget
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Budget Cards Grid */}
      {!isLoading && statuses.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {statuses.map((budget) => (
            <BudgetCard
              key={budget.id}
              budget={budget}
              onEdit={handleEditClick}
              onDelete={handleDeleteClick}
            />
          ))}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-5 space-y-4">
                <div className="h-6 bg-gray-200 rounded w-1/3"></div>
                <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                <div className="h-3 bg-gray-200 rounded"></div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="h-8 bg-gray-200 rounded"></div>
                  <div className="h-8 bg-gray-200 rounded"></div>
                  <div className="h-8 bg-gray-200 rounded"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Budget Form Dialog */}
      <BudgetFormDialog
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        budget={editingBudget}
        categories={categories}
        onSubmit={handleFormSubmit}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleDeleteConfirm}
        budgetName={deletingBudgetName}
      />
    </div>
  );
}
