import * as React from 'react';
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { 
  WealthOverview, 
  SavingsGoalCard, 
  ProjectionSimulator,
  WealthDistribution 
} from '@/components/wealth';
import { useWealthAccounts, useSavingsGoals } from '@/hooks/useWealth';
import type { WealthAccount, SavingsGoal } from '@/types/wealth';

// Icons
const PlusIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
    <path d="M5 12h14"/><path d="M12 5v14"/>
  </svg>
);

const PiggyBankIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 5c-1.5 0-2.8 1.4-3 2-3.5-1.5-11-.3-11 5 0 1.8 0 3 2 4.5V20h4v-2h3v2h4v-4c1-.5 1.7-1 2-2h2v-4h-2c0-1-.5-1.5-1-2h0V5z"/>
    <path d="M2 9v1c0 1.1.9 2 2 2h1"/>
    <path d="M16 11h0"/>
  </svg>
);

const TargetIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
  </svg>
);

const TrendingUpIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
  </svg>
);

const PieChartIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/>
  </svg>
);

// Format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount);
};

// Composant formulaire pour ajouter un objectif
interface GoalFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: Partial<SavingsGoal>) => void;
  goal?: SavingsGoal | null;
}

function GoalFormDialog({ open, onOpenChange, onSubmit, goal }: GoalFormDialogProps) {
  const [formData, setFormData] = useState<Partial<SavingsGoal>>({
    name: '',
    target_amount: 0,
    current_amount: 0,
    deadline: '',
    category: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  React.useEffect(() => {
    if (goal) {
      setFormData({
        name: goal.name,
        target_amount: goal.target_amount,
        current_amount: goal.current_amount,
        deadline: goal.deadline,
        category: goal.category,
      });
    } else {
      setFormData({
        name: '',
        target_amount: 0,
        current_amount: 0,
        deadline: '',
        category: '',
      });
    }
    setErrors({});
  }, [goal, open]);

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name?.trim()) {
      newErrors.name = 'Le nom est requis';
    }
    if (!formData.target_amount || formData.target_amount <= 0) {
      newErrors.target_amount = 'Le montant cible doit être supérieur à 0';
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{goal ? 'Modifier l\'objectif' : 'Nouvel objectif d\'épargne'}</DialogTitle>
            <DialogDescription>
              {goal 
                ? 'Modifiez les détails de votre objectif.' 
                : 'Définissez un nouvel objectif d\'épargne.'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Nom */}
            <div className="space-y-2">
              <Label htmlFor="name">Nom de l'objectif</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Ex: Vacances, Nouvelle voiture..."
              />
              {errors.name && <p className="text-sm text-red-500">{errors.name}</p>}
            </div>

            {/* Montant cible */}
            <div className="space-y-2">
              <Label htmlFor="target">Montant cible (€)</Label>
              <Input
                id="target"
                type="number"
                min="0"
                step="100"
                value={formData.target_amount || ''}
                onChange={(e) => setFormData({ ...formData, target_amount: parseFloat(e.target.value) })}
                placeholder="0.00"
              />
              {errors.target_amount && <p className="text-sm text-red-500">{errors.target_amount}</p>}
            </div>

            {/* Montant actuel */}
            <div className="space-y-2">
              <Label htmlFor="current">Montant actuel (€)</Label>
              <Input
                id="current"
                type="number"
                min="0"
                step="100"
                value={formData.current_amount || ''}
                onChange={(e) => setFormData({ ...formData, current_amount: parseFloat(e.target.value) })}
                placeholder="0.00"
              />
            </div>

            {/* Date butoir */}
            <div className="space-y-2">
              <Label htmlFor="deadline">Date butoir</Label>
              <Input
                id="deadline"
                type="date"
                value={formData.deadline || ''}
                onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
              />
            </div>

            {/* Catégorie */}
            <div className="space-y-2">
              <Label htmlFor="category">Catégorie (optionnel)</Label>
              <Input
                id="category"
                value={formData.category || ''}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="Ex: Voyage, Achat..."
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Annuler
            </Button>
            <Button type="submit">
              {goal ? 'Mettre à jour' : 'Créer l\'objectif'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// Composant formulaire pour ajouter un compte
interface AccountFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: Partial<WealthAccount>) => void;
}

function AccountFormDialog({ open, onOpenChange, onSubmit }: AccountFormDialogProps) {
  const [formData, setFormData] = useState<Partial<WealthAccount>>({
    name: '',
    type: 'checking',
    balance: 0,
    institution: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name?.trim()) {
      newErrors.name = 'Le nom est requis';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
      onOpenChange(false);
      setFormData({ name: '', type: 'checking', balance: 0, institution: '' });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Nouveau compte</DialogTitle>
            <DialogDescription>
              Ajoutez un compte à votre patrimoine.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Nom */}
            <div className="space-y-2">
              <Label htmlFor="acc-name">Nom du compte</Label>
              <Input
                id="acc-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Ex: Livret A, PEA..."
              />
              {errors.name && <p className="text-sm text-red-500">{errors.name}</p>}
            </div>

            {/* Type */}
            <div className="space-y-2">
              <Label htmlFor="acc-type">Type</Label>
              <Select
                id="acc-type"
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
              >
                <option value="checking">💰 Liquidités (Compte courant)</option>
                <option value="savings">🏦 Épargne (Livret, LEP...)</option>
                <option value="investment">📈 Investissements (PEA, CTO...)</option>
                <option value="crypto">₿ Crypto</option>
                <option value="other">📦 Autre</option>
              </Select>
            </div>

            {/* Solde */}
            <div className="space-y-2">
              <Label htmlFor="acc-balance">Solde actuel (€)</Label>
              <Input
                id="acc-balance"
                type="number"
                min="0"
                step="0.01"
                value={formData.balance || ''}
                onChange={(e) => setFormData({ ...formData, balance: parseFloat(e.target.value) })}
                placeholder="0.00"
              />
            </div>

            {/* Institution */}
            <div className="space-y-2">
              <Label htmlFor="acc-institution">Institution (optionnel)</Label>
              <Input
                id="acc-institution"
                value={formData.institution || ''}
                onChange={(e) => setFormData({ ...formData, institution: e.target.value })}
                placeholder="Ex: Banque Populaire, Binance..."
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Annuler
            </Button>
            <Button type="submit">Ajouter le compte</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// Dialogue pour contribuer à un objectif
interface ContributeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (amount: number) => void;
  goalName?: string;
}

function ContributeDialog({ open, onOpenChange, onConfirm, goalName }: ContributeDialogProps) {
  const [amount, setAmount] = useState(100);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onConfirm(amount);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Contribuer à l'objectif</DialogTitle>
            <DialogDescription>
              Ajoutez un montant à <strong>{goalName}</strong>
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <Label htmlFor="contrib-amount">Montant (€)</Label>
            <Input
              id="contrib-amount"
              type="number"
              min="1"
              step="10"
              value={amount}
              onChange={(e) => setAmount(parseFloat(e.target.value))}
              className="mt-2"
              autoFocus
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Annuler
            </Button>
            <Button type="submit">Contribuer</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// Page principale
export function Wealth() {
  const { 
    accounts, 
    stats, 
    isLoading: accountsLoading, 
    error: accountsError, 
    addAccount 
  } = useWealthAccounts();
  
  const { 
    goals, 
    isLoading: goalsLoading, 
    error: goalsError, 
    addGoal, 
    editGoal,
    contributeToGoal 
  } = useSavingsGoals();

  const [activeTab, setActiveTab] = useState('overview');
  const [isGoalFormOpen, setIsGoalFormOpen] = useState(false);
  const [isAccountFormOpen, setIsAccountFormOpen] = useState(false);
  const [isContributeOpen, setIsContributeOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState<SavingsGoal | null>(null);
  const [selectedGoalId, setSelectedGoalId] = useState<number | null>(null);
  const [selectedGoalName, setSelectedGoalName] = useState('');

  const isLoading = accountsLoading || goalsLoading;
  const error = accountsError || goalsError;

  const handleAddGoal = () => {
    setEditingGoal(null);
    setIsGoalFormOpen(true);
  };

  const handleEditGoal = (goal: SavingsGoal) => {
    setEditingGoal(goal);
    setIsGoalFormOpen(true);
  };

  const handleGoalSubmit = async (data: Partial<SavingsGoal>) => {
    try {
      if (editingGoal) {
        await editGoal(editingGoal.id, data);
      } else {
        await addGoal(data);
      }
    } catch (err) {
      console.error('Error saving goal:', err);
    }
  };

  const handleContribute = (id: number) => {
    const goal = goals.find(g => g.id === id);
    setSelectedGoalId(id);
    setSelectedGoalName(goal?.name || '');
    setIsContributeOpen(true);
  };

  const handleContributeConfirm = async (amount: number) => {
    if (selectedGoalId) {
      await contributeToGoal(selectedGoalId, amount);
    }
  };

  const handleAccountSubmit = async (data: Partial<WealthAccount>) => {
    try {
      await addAccount(data);
    } catch (err) {
      console.error('Error adding account:', err);
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Patrimoine</h1>
          <p className="text-gray-500 mt-1">Suivez votre patrimoine et planifiez vos objectifs</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setIsAccountFormOpen(true)}>
            <PlusIcon />
            Compte
          </Button>
          <Button onClick={handleAddGoal}>
            <PlusIcon />
            Objectif
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTitle>Erreur</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Vue d'ensemble KPIs */}
      <WealthOverview />

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <PiggyBankIcon />
            <span className="hidden sm:inline">Objectifs</span>
          </TabsTrigger>
          <TabsTrigger value="simulator" className="flex items-center gap-2">
            <TrendingUpIcon />
            <span className="hidden sm:inline">Simulateur</span>
          </TabsTrigger>
          <TabsTrigger value="distribution" className="flex items-center gap-2">
            <PieChartIcon />
            <span className="hidden sm:inline">Répartition</span>
          </TabsTrigger>
        </TabsList>

        {/* Tab: Objectifs */}
        <TabsContent value="overview" className="space-y-6">
          {/* Objectifs d'épargne */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <TargetIcon />
                  Objectifs d'épargne
                </CardTitle>
                <Button size="sm" onClick={handleAddGoal}>
                  <PlusIcon />
                  Ajouter
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[1, 2, 3].map((i) => (
                    <Card key={i} className="animate-pulse">
                      <CardContent className="p-5 space-y-4">
                        <div className="h-6 bg-gray-200 rounded w-1/2"></div>
                        <div className="h-3 bg-gray-200 rounded"></div>
                        <div className="h-8 bg-gray-200 rounded"></div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : goals.length === 0 ? (
                <div className="text-center py-12">
                  <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                    <TargetIcon />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Aucun objectif défini
                  </h3>
                  <p className="text-gray-500 mb-4 max-w-md mx-auto">
                    Créez votre premier objectif d'épargne pour suivre vos projets.
                  </p>
                  <Button onClick={handleAddGoal}>
                    <PlusIcon />
                    Créer mon premier objectif
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {goals.map((goal) => (
                    <SavingsGoalCard
                      key={goal.id}
                      goal={goal}
                      onContribute={handleContribute}
                      onEdit={handleEditGoal}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Simulateur */}
        <TabsContent value="simulator">
          <ProjectionSimulator initialInitialAmount={stats.totalWealth} />
        </TabsContent>

        {/* Tab: Répartition */}
        <TabsContent value="distribution">
          <WealthDistribution />
        </TabsContent>
      </Tabs>

      {/* Dialogues */}
      <GoalFormDialog
        open={isGoalFormOpen}
        onOpenChange={setIsGoalFormOpen}
        goal={editingGoal}
        onSubmit={handleGoalSubmit}
      />

      <AccountFormDialog
        open={isAccountFormOpen}
        onOpenChange={setIsAccountFormOpen}
        onSubmit={handleAccountSubmit}
      />

      <ContributeDialog
        open={isContributeOpen}
        onOpenChange={setIsContributeOpen}
        onConfirm={handleContributeConfirm}
        goalName={selectedGoalName}
      />
    </div>
  );
}
