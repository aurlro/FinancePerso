import * as React from 'react';
import { useState, useEffect, useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { useSubscriptions, useUpcomingPayments } from '@/hooks/useSubscriptions';
import { useIPC } from '@/hooks/useIPC';
import type { Subscription, DetectedSubscription, Category } from '@/types';

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

const SearchIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
  </svg>
);

const CalendarIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/>
  </svg>
);

// Category colors mapping
const categoryColors: Record<string, string> = {
  'Alimentation': '#ef4444',
  'Transport': '#f97316',
  'Logement': '#8b5cf6',
  'Santé': '#ec4899',
  'Loisirs': '#14b8a6',
  'Shopping': '#f59e0b',
  'Revenus': '#10b981',
  'Autre': '#6b7280',
};

// Format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount);
};

// Format date
const formatDate = (dateStr?: string) => {
  if (!dateStr) return 'Non défini';
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat('fr-FR', { 
    day: 'numeric', 
    month: 'long',
    year: 'numeric'
  }).format(date);
};

// Calculate days until payment
const getDaysUntil = (dateStr?: string) => {
  if (!dateStr) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const paymentDate = new Date(dateStr);
  paymentDate.setHours(0, 0, 0, 0);
  const diffTime = paymentDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
};

// Get frequency label
const getFrequencyLabel = (frequency: string) => {
  switch (frequency) {
    case 'monthly': return '/mois';
    case 'yearly': return '/an';
    case 'weekly': return '/semaine';
    default: return '/mois';
  }
};

// Get emoji for subscription name
const getSubscriptionEmoji = (name: string) => {
  const emojis: Record<string, string> = {
    'NETFLIX': '🎬',
    'SPOTIFY': '🎵',
    'AMAZON': '📦',
    'PRIME': '📦',
    'DISNEY': '🏰',
    'CANAL': '📺',
    'OCS': '🎞️',
    'YOUTUBE': '▶️',
    'ADOBE': '🎨',
    'MICROSOFT': '💻',
    'OFFICE': '📝',
    'GOOGLE': '🔍',
    'DROPBOX': '📁',
    'APPLE': '🍎',
    'ICLOUD': '☁️',
    'EDF': '⚡',
    'ENGIE': '🔥',
    'TOTAL': '⛽',
    'FREE': '📱',
    'ORANGE': '📡',
    'SFR': '📶',
    'BOUYGUES': '📲',
    'GYM': '💪',
    'FITNESS': '🏋️',
    'JOURNAL': '📰',
    'MONDE': '📰',
    'FIGARO': '📰',
  };
  
  const upperName = name.toUpperCase();
  for (const [key, emoji] of Object.entries(emojis)) {
    if (upperName.includes(key)) return emoji;
  }
  return '📋';
};

// Subscription Card Component
interface SubscriptionCardProps {
  subscription: Subscription;
  onEdit: (subscription: Subscription) => void;
  onDelete: (id: number) => void;
}

function SubscriptionCard({ subscription, onEdit, onDelete }: SubscriptionCardProps) {
  const daysUntil = getDaysUntil(subscription.next_payment_date);
  const categoryColor = categoryColors[subscription.category || 'Autre'] || '#6b7280';
  const emoji = getSubscriptionEmoji(subscription.name);
  
  let urgencyBadge = null;
  if (daysUntil !== null) {
    if (daysUntil < 0) {
      urgencyBadge = <Badge variant="danger">En retard</Badge>;
    } else if (daysUntil === 0) {
      urgencyBadge = <Badge variant="warning">Aujourd'hui</Badge>;
    } else if (daysUntil <= 7) {
      urgencyBadge = <Badge variant="warning">Cette semaine</Badge>;
    } else if (daysUntil <= 30) {
      urgencyBadge = <Badge variant="info">Ce mois</Badge>;
    }
  }

  return (
    <Card className="relative overflow-hidden transition-shadow hover:shadow-md" style={{ borderLeftColor: categoryColor, borderLeftWidth: '4px' }}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center text-2xl">
              {emoji}
            </div>
            <div>
              <h3 className="font-semibold text-lg text-gray-900">{subscription.name}</h3>
              <p className="text-sm text-gray-500">{subscription.category || 'Non catégorisé'}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {urgencyBadge}
          </div>
        </div>

        {/* Amount */}
        <div className="mb-4">
          <p className="text-2xl font-bold text-gray-900">
            {formatCurrency(subscription.amount)}
            <span className="text-sm font-normal text-gray-500">{getFrequencyLabel(subscription.frequency)}</span>
          </p>
        </div>

        {/* Next payment */}
        {subscription.next_payment_date && (
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
            <CalendarIcon />
            <span>
              Prochain: {formatDate(subscription.next_payment_date)}
              {daysUntil !== null && daysUntil >= 0 && (
                <span className="text-gray-400"> (dans {daysUntil} jour{daysUntil > 1 ? 's' : ''})</span>
              )}
            </span>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2 pt-3 border-t border-gray-100">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onEdit(subscription)}
            className="flex-1"
          >
            <EditIcon />
            Modifier
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete(subscription.id)}
            className="text-red-500 hover:text-red-600 hover:bg-red-50"
          >
            <TrashIcon />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// Subscription Form Dialog
interface SubscriptionFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  subscription?: Subscription | null;
  categories: Category[];
  onSubmit: (data: Partial<Subscription>) => void;
}

function SubscriptionFormDialog({ open, onOpenChange, subscription, categories, onSubmit }: SubscriptionFormDialogProps) {
  const [formData, setFormData] = useState<Partial<Subscription>>({
    name: '',
    amount: 0,
    frequency: 'monthly',
    category: '',
    next_payment_date: '',
    provider: '',
    is_active: 1,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (subscription) {
      setFormData({
        name: subscription.name,
        amount: subscription.amount,
        frequency: subscription.frequency,
        category: subscription.category,
        next_payment_date: subscription.next_payment_date,
        provider: subscription.provider,
        is_active: subscription.is_active,
      });
    } else {
      // Default next payment date to today + 1 month
      const nextMonth = new Date();
      nextMonth.setMonth(nextMonth.getMonth() + 1);
      
      setFormData({
        name: '',
        amount: 0,
        frequency: 'monthly',
        category: '',
        next_payment_date: nextMonth.toISOString().split('T')[0],
        provider: '',
        is_active: 1,
      });
    }
    setErrors({});
  }, [subscription, open]);

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name?.trim()) {
      newErrors.name = 'Veuillez entrer un nom';
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{subscription ? 'Modifier l\'abonnement' : 'Nouvel abonnement'}</DialogTitle>
            <DialogDescription>
              {subscription 
                ? 'Modifiez les détails de votre abonnement.' 
                : 'Ajoutez un nouvel abonnement à suivre.'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Nom *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Netflix, Spotify, EDF..."
              />
              {errors.name && (
                <p className="text-sm text-red-500">{errors.name}</p>
              )}
            </div>

            {/* Amount & Frequency */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="amount">Montant (€) *</Label>
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
              <div className="space-y-2">
                <Label htmlFor="frequency">Fréquence</Label>
                <Select
                  id="frequency"
                  value={formData.frequency}
                  onChange={(e) => setFormData({ ...formData, frequency: e.target.value as Subscription['frequency'] })}
                >
                  <option value="monthly">Mensuel</option>
                  <option value="yearly">Annuel</option>
                  <option value="weekly">Hebdomadaire</option>
                </Select>
              </div>
            </div>

            {/* Category */}
            <div className="space-y-2">
              <Label htmlFor="category">Catégorie</Label>
              <Select
                id="category"
                value={formData.category || ''}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              >
                <option value="">Non catégorisé</option>
                {categories.map((cat) => (
                  <option key={cat.name} value={cat.name}>
                    {cat.emoji} {cat.name}
                  </option>
                ))}
              </Select>
            </div>

            {/* Next Payment Date */}
            <div className="space-y-2">
              <Label htmlFor="next_payment_date">Prochain paiement</Label>
              <Input
                id="next_payment_date"
                type="date"
                value={formData.next_payment_date || ''}
                onChange={(e) => setFormData({ ...formData, next_payment_date: e.target.value })}
              />
            </div>

            {/* Status */}
            <div className="space-y-2">
              <Label htmlFor="status">Statut</Label>
              <Select
                id="status"
                value={formData.is_active === 1 ? 'active' : 'inactive'}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.value === 'active' ? 1 : 0 })}
              >
                <option value="active">✅ Actif</option>
                <option value="inactive">⏸️ Inactif</option>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Annuler
            </Button>
            <Button type="submit">
              {subscription ? 'Mettre à jour' : 'Créer l\'abonnement'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// Detection Dialog
interface DetectionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  detected: DetectedSubscription[];
  onImport: (detected: DetectedSubscription) => void;
  isLoading: boolean;
}

function DetectionDialog({ open, onOpenChange, detected, onImport, isLoading }: DetectionDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <SearchIcon />
            Abonnements détectés
          </DialogTitle>
          <DialogDescription>
            {detected.length > 0 
              ? `${detected.length} abonnement${detected.length > 1 ? 's' : ''} potentiel${detected.length > 1 ? 's' : ''} trouvé${detected.length > 1 ? 's' : ''} dans vos transactions.`
              : 'Aucun abonnement détecté automatiquement.'}
          </DialogDescription>
        </DialogHeader>

        {isLoading ? (
          <div className="py-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-500">Analyse des transactions en cours...</p>
          </div>
        ) : (
          <div className="space-y-3 py-4">
            {detected.length === 0 ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🔍</span>
                </div>
                <p className="text-gray-500">
                  Aucun pattern régulier détecté dans vos transactions.
                  <br />
                  Essayez d'ajouter manuellement vos abonnements.
                </p>
              </div>
            ) : (
              detected.map((item, index) => (
                <Card key={index} className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center text-xl">
                        {getSubscriptionEmoji(item.name)}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{item.name}</h4>
                        <p className="text-sm text-gray-500">
                          {formatCurrency(item.amount)} {getFrequencyLabel(item.frequency)}
                          {' · '}
                          {item.transactions.length} transactions
                          {' · '}
                          Confiance: {Math.round(item.confidence * 100)}%
                        </p>
                        {item.category && (
                          <Badge variant="outline" className="mt-1">
                            {item.category}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <Button 
                      size="sm" 
                      onClick={() => onImport(item)}
                      variant="outline"
                    >
                      <PlusIcon />
                      Ajouter
                    </Button>
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        <DialogFooter>
          <Button onClick={() => onOpenChange(false)}>
            Fermer
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Delete Confirmation Dialog
interface DeleteDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  subscriptionName?: string;
}

function DeleteDialog({ open, onOpenChange, onConfirm, subscriptionName }: DeleteDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-red-600">
            <AlertTriangleIcon />
            Confirmer la suppression
          </DialogTitle>
          <DialogDescription>
            Êtes-vous sûr de vouloir supprimer l'abonnement <strong>{subscriptionName}</strong> ?
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

// Alerts Section
function AlertsSection({ subscriptions }: { subscriptions: Subscription[] }) {
  const alerts = useMemo(() => {
    const result: { type: string; message: string; severity: 'info' | 'warning' | 'danger' }[] = [];
    
    // Check for upcoming payments this week
    const thisWeek = subscriptions.filter(s => {
      const days = getDaysUntil(s.next_payment_date);
      return days !== null && days >= 0 && days <= 7;
    });
    
    if (thisWeek.length > 0) {
      result.push({
        type: 'upcoming',
        message: `${thisWeek.length} abonnement${thisWeek.length > 1 ? 's' : ''} à payer cette semaine`,
        severity: 'warning',
      });
    }
    
    // Check for potential duplicates (same amount, similar name)
    const duplicates: string[] = [];
    for (let i = 0; i < subscriptions.length; i++) {
      for (let j = i + 1; j < subscriptions.length; j++) {
        const s1 = subscriptions[i];
        const s2 = subscriptions[j];
        if (Math.abs(s1.amount - s2.amount) < 0.01 && s1.frequency === s2.frequency) {
          duplicates.push(`${s1.name} / ${s2.name}`);
        }
      }
    }
    
    if (duplicates.length > 0) {
      result.push({
        type: 'duplicate',
        message: `Doublons potentiels détectés: ${duplicates.slice(0, 2).join(', ')}${duplicates.length > 2 ? '...' : ''}`,
        severity: 'info',
      });
    }
    
    return result;
  }, [subscriptions]);

  if (alerts.length === 0) return null;

  return (
    <div className="space-y-3">
      {alerts.map((alert, index) => (
        <Alert 
          key={index} 
          variant={alert.severity === 'danger' ? 'destructive' : alert.severity === 'warning' ? 'default' : 'default'}
          className={alert.severity === 'warning' ? 'border-amber-500 bg-amber-50' : alert.severity === 'info' ? 'border-blue-500 bg-blue-50' : ''}
        >
          <AlertTitle className="flex items-center gap-2">
            {alert.severity === 'warning' && <AlertTriangleIcon />}
            {alert.type === 'upcoming' ? 'Paiements à venir' : 'Doublons détectés'}
          </AlertTitle>
          <AlertDescription>{alert.message}</AlertDescription>
        </Alert>
      ))}
    </div>
  );
}

// Main Subscriptions Page
export function Subscriptions() {
  const { getCategories } = useIPC();
  const { 
    subscriptions, 
    isLoading, 
    isDetecting, 
    error, 
    addSubscription, 
    editSubscription, 
    removeSubscription,
    runDetection,
  } = useSubscriptions();
  const { upcoming } = useUpcomingPayments(30);
  const [categories, setCategories] = useState<Category[]>([]);
  
  // Dialog states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingSubscription, setEditingSubscription] = useState<Subscription | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deletingSubscriptionId, setDeletingSubscriptionId] = useState<number | null>(null);
  const [deletingSubscriptionName, setDeletingSubscriptionName] = useState('');
  const [detectionDialogOpen, setDetectionDialogOpen] = useState(false);
  const [detectedSubscriptions, setDetectedSubscriptions] = useState<DetectedSubscription[]>([]);

  // Load categories
  useEffect(() => {
    getCategories().then(setCategories);
  }, [getCategories]);

  // Action handlers
  const handleAddClick = () => {
    setEditingSubscription(null);
    setIsFormOpen(true);
  };

  const handleEditClick = (subscription: Subscription) => {
    setEditingSubscription(subscription);
    setIsFormOpen(true);
  };

  const handleDeleteClick = (id: number) => {
    const subscription = subscriptions.find(s => s.id === id);
    setDeletingSubscriptionId(id);
    setDeletingSubscriptionName(subscription?.name || '');
    setDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data: Partial<Subscription>) => {
    try {
      if (editingSubscription) {
        await editSubscription(editingSubscription.id, data);
      } else {
        await addSubscription(data);
      }
    } catch (err) {
      console.error('Error saving subscription:', err);
    }
  };

  const handleDeleteConfirm = async () => {
    if (deletingSubscriptionId) {
      try {
        await removeSubscription(deletingSubscriptionId);
        setDeleteDialogOpen(false);
      } catch (err) {
        console.error('Error deleting subscription:', err);
      }
    }
  };

  const handleDetectClick = async () => {
    try {
      const detected = await runDetection();
      setDetectedSubscriptions(detected);
      setDetectionDialogOpen(true);
    } catch (err) {
      console.error('Error detecting subscriptions:', err);
    }
  };

  const handleImportDetected = async (detected: DetectedSubscription) => {
    try {
      // Calculate next payment date based on frequency
      const nextDate = new Date();
      switch (detected.frequency) {
        case 'monthly':
          nextDate.setMonth(nextDate.getMonth() + 1);
          break;
        case 'yearly':
          nextDate.setFullYear(nextDate.getFullYear() + 1);
          break;
        case 'weekly':
          nextDate.setDate(nextDate.getDate() + 7);
          break;
      }
      
      await addSubscription({
        name: detected.name,
        amount: detected.amount,
        frequency: detected.frequency,
        category: detected.category,
        next_payment_date: nextDate.toISOString().split('T')[0],
        provider: detected.provider,
        is_active: 1,
      });
      
      // Remove from detected list
      setDetectedSubscriptions(prev => prev.filter(d => d.name !== detected.name));
    } catch (err) {
      console.error('Error importing subscription:', err);
    }
  };

  // Calculate totals
  const monthlyTotal = subscriptions
    .filter(s => s.frequency === 'monthly' && s.is_active === 1)
    .reduce((sum, s) => sum + s.amount, 0);
  
  const yearlyTotal = subscriptions
    .filter(s => s.is_active === 1)
    .reduce((sum, s) => {
      switch (s.frequency) {
        case 'monthly': return sum + (s.amount * 12);
        case 'yearly': return sum + s.amount;
        case 'weekly': return sum + (s.amount * 52);
        default: return sum;
      }
    }, 0);

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Abonnements</h1>
          <p className="text-gray-500 mt-1">Suivez vos abonnements et paiements récurrents</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleDetectClick} disabled={isDetecting}>
            <SearchIcon />
            {isDetecting ? 'Détection...' : 'Détection auto'}
          </Button>
          <Button onClick={handleAddClick}>
            <PlusIcon />
            Ajouter
          </Button>
        </div>
      </div>

      {/* Alerts */}
      <AlertsSection subscriptions={subscriptions} />

      {/* Summary Cards */}
      {subscriptions.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500">Ce mois</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(monthlyTotal)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500">Cette année (estimé)</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(yearlyTotal)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500">Paiements ce mois</p>
              <p className="text-2xl font-bold text-emerald-600">{upcoming.length}</p>
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
      {!isLoading && subscriptions.length === 0 && !error && (
        <Card className="py-12">
          <CardContent className="text-center">
            <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl">📅</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Aucun abonnement
            </h3>
            <p className="text-gray-500 mb-4 max-w-md mx-auto">
              Commencez par ajouter vos abonnements ou utilisez la détection automatique.
            </p>
            <div className="flex gap-2 justify-center">
              <Button variant="outline" onClick={handleDetectClick} disabled={isDetecting}>
                <SearchIcon />
                {isDetecting ? 'Détection...' : 'Détection auto'}
              </Button>
              <Button onClick={handleAddClick}>
                <PlusIcon />
                Ajouter manuellement
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Subscription Cards Grid */}
      {!isLoading && subscriptions.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {subscriptions.map((subscription) => (
            <SubscriptionCard
              key={subscription.id}
              subscription={subscription}
              onEdit={handleEditClick}
              onDelete={handleDeleteClick}
            />
          ))}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-5 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
                  <div className="space-y-2">
                    <div className="h-5 bg-gray-200 rounded w-32"></div>
                    <div className="h-4 bg-gray-200 rounded w-24"></div>
                  </div>
                </div>
                <div className="h-8 bg-gray-200 rounded w-1/3"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Subscription Form Dialog */}
      <SubscriptionFormDialog
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        subscription={editingSubscription}
        categories={categories}
        onSubmit={handleFormSubmit}
      />

      {/* Detection Dialog */}
      <DetectionDialog
        open={detectionDialogOpen}
        onOpenChange={setDetectionDialogOpen}
        detected={detectedSubscriptions}
        onImport={handleImportDetected}
        isLoading={isDetecting}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleDeleteConfirm}
        subscriptionName={deletingSubscriptionName}
      />
    </div>
  );
}
