import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useMembers, useMemberStats } from '@/hooks/useMembers';
import { Member, MemberStats } from '@/types';
import { Plus, Edit2, Trash2, Crown, User } from 'lucide-react';
import { cn } from '@/lib/utils';

const MEMBER_COLORS = [
  { value: '#8b5cf6', label: 'Violet' },
  { value: '#06b6d4', label: 'Cyan' },
  { value: '#10b981', label: 'Emerald' },
  { value: '#f59e0b', label: 'Ambre' },
  { value: '#ef4444', label: 'Rouge' },
  { value: '#ec4899', label: 'Rose' },
];

const MEMBER_EMOJIS = ['👤', '👥', '👨', '👩', '🧑', '🙂', '👶', '🐱', '🐶'];

interface MemberFormData {
  name: string;
  type: 'primary' | 'secondary';
  color: string;
  emoji: string;
  email: string;
}

function MemberBadge({ member, size = 'md', showName = false }: { member: Member; size?: 'sm' | 'md' | 'lg'; showName?: boolean }) {
  const sizeClasses = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-10 h-10 text-lg',
    lg: 'w-16 h-16 text-2xl',
  };

  return (
    <div className="flex items-center gap-2">
      <div
        className={cn(
          'rounded-full flex items-center justify-center border-2',
          sizeClasses[size]
        )}
        style={{ 
          backgroundColor: `${member.color}20`,
          borderColor: member.color 
        }}
      >
        <span>{member.emoji}</span>
      </div>
      {showName && (
        <div className="flex flex-col">
          <span className="font-medium text-sm">{member.name}</span>
          {member.type === 'primary' && (
            <span className="text-xs text-emerald-600 flex items-center gap-1">
              <Crown className="w-3 h-3" /> Principal
            </span>
          )}
        </div>
      )}
    </div>
  );
}

function MemberBarChart({ stats, totalExpense }: { stats: MemberStats[]; totalExpense: number }) {
  if (stats.length === 0 || totalExpense === 0) {
    return (
      <div className="text-center text-muted-foreground py-8">
        Aucune dépense ce mois-ci
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {stats.map((member) => {
        const percentage = totalExpense > 0 ? (member.total / totalExpense) * 100 : 0;
        return (
          <div key={member.id} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="text-lg">{member.emoji}</span>
                <span className="font-medium">{member.name}</span>
                {member.type === 'primary' && (
                  <Crown className="w-3 h-3 text-amber-500" />
                )}
              </div>
              <div className="flex items-center gap-4">
                <span className="text-muted-foreground">{percentage.toFixed(1)}%</span>
                <span className="font-bold w-20 text-right">{member.total.toFixed(2)}€</span>
              </div>
            </div>
            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{ 
                  width: `${Math.min(percentage, 100)}%`,
                  backgroundColor: member.color 
                }}
              />
            </div>
            <div className="text-xs text-muted-foreground text-right">
              {member.transaction_count} transaction{member.transaction_count > 1 ? 's' : ''}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function MemberForm({ 
  initialData, 
  onSubmit, 
  onCancel,
  isEditing = false 
}: { 
  initialData?: Partial<MemberFormData>; 
  onSubmit: (data: MemberFormData) => void;
  onCancel: () => void;
  isEditing?: boolean;
}) {
  const [formData, setFormData] = React.useState<MemberFormData>({
    name: initialData?.name || '',
    type: initialData?.type || 'secondary',
    color: initialData?.color || '#8b5cf6',
    emoji: initialData?.emoji || '👤',
    email: initialData?.email || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Nom</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="Prénom"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="type">Type</Label>
        <Select
          value={formData.type}
          onValueChange={(value: 'primary' | 'secondary') => setFormData({ ...formData, type: value })}
          disabled={isEditing}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="primary">Principal</SelectItem>
            <SelectItem value="secondary">Secondaire</SelectItem>
          </SelectContent>
        </Select>
        {!isEditing && (
          <p className="text-xs text-muted-foreground">
            Le membre principal ne peut pas être supprimé.
          </p>
        )}
      </div>

      <div className="space-y-2">
        <Label>Couleur</Label>
        <div className="flex flex-wrap gap-2">
          {MEMBER_COLORS.map((c) => (
            <button
              key={c.value}
              type="button"
              onClick={() => setFormData({ ...formData, color: c.value })}
              className={cn(
                'w-8 h-8 rounded-full border-2 transition-all',
                formData.color === c.value ? 'border-gray-900 scale-110' : 'border-transparent'
              )}
              style={{ backgroundColor: c.value }}
              title={c.label}
            />
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <Label>Icône</Label>
        <div className="flex flex-wrap gap-2">
          {MEMBER_EMOJIS.map((emoji) => (
            <button
              key={emoji}
              type="button"
              onClick={() => setFormData({ ...formData, emoji })}
              className={cn(
                'w-10 h-10 rounded-lg border-2 text-xl transition-all hover:bg-gray-50',
                formData.emoji === emoji ? 'border-emerald-500 bg-emerald-50' : 'border-gray-200'
              )}
            >
              {emoji}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email (optionnel)</Label>
        <Input
          id="email"
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          placeholder="email@exemple.com"
        />
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Annuler
        </Button>
        <Button type="submit">
          {isEditing ? 'Mettre à jour' : 'Créer'}
        </Button>
      </div>
    </form>
  );
}

export function Members() {
  const { members, loading, error, refresh, addMember, updateMember, removeMember } = useMembers();
  const { stats, loading: statsLoading } = useMemberStats(
    new Date().getFullYear(),
    new Date().getMonth() + 1
  );
  const [isAddDialogOpen, setIsAddDialogOpen] = React.useState(false);
  const [editingMember, setEditingMember] = React.useState<Member | null>(null);
  const [deletingMember, setDeletingMember] = React.useState<Member | null>(null);

  const totalExpense = React.useMemo(() => {
    return stats.reduce((sum, s) => sum + s.total, 0);
  }, [stats]);

  const handleAdd = async (formData: MemberFormData) => {
    const success = await addMember(formData);
    if (success) {
      setIsAddDialogOpen(false);
    }
  };

  const handleUpdate = async (formData: MemberFormData) => {
    if (!editingMember) return;
    const success = await updateMember(editingMember.id, formData);
    if (success) {
      setEditingMember(null);
    }
  };

  const handleDelete = async () => {
    if (!deletingMember) return;
    const success = await removeMember(deletingMember.id);
    if (success) {
      setDeletingMember(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-8 text-red-600">
        <p>Erreur: {error}</p>
        <Button onClick={refresh} variant="outline" className="mt-4">
          Réessayer
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Membres du foyer</h2>
          <p className="text-muted-foreground">
            {members.length} membre{members.length > 1 ? 's' : ''}
          </p>
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Ajouter un membre
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Nouveau membre</DialogTitle>
            </DialogHeader>
            <MemberForm
              onSubmit={handleAdd}
              onCancel={() => setIsAddDialogOpen(false)}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Répartition des dépenses par membre</CardTitle>
        </CardHeader>
        <CardContent>
          {statsLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-500" />
            </div>
          ) : (
            <MemberBarChart stats={stats} totalExpense={totalExpense} />
          )}
        </CardContent>
      </Card>

      {/* Members Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {members.map((member) => {
          const memberStat = stats.find(s => s.id === member.id);
          return (
            <Card key={member.id} className="group hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <MemberBadge member={member} size="lg" showName />
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => setEditingMember(member)}
                    >
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    {member.type !== 'primary' && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => setDeletingMember(member)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </div>

                {memberStat && memberStat.total > 0 && (
                  <div className="mt-4 pt-4 border-t">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Dépenses ce mois</span>
                      <span className="font-bold">{memberStat.total.toFixed(2)}€</span>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {memberStat.transaction_count} transaction{memberStat.transaction_count > 1 ? 's' : ''}
                    </div>
                  </div>
                )}

                {member.email && (
                  <div className="mt-2 text-sm text-muted-foreground truncate">
                    {member.email}
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Edit Dialog */}
      <Dialog open={!!editingMember} onOpenChange={() => setEditingMember(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Modifier le membre</DialogTitle>
          </DialogHeader>
          {editingMember && (
            <MemberForm
              initialData={editingMember}
              onSubmit={handleUpdate}
              onCancel={() => setEditingMember(null)}
              isEditing
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <Dialog open={!!deletingMember} onOpenChange={() => setDeletingMember(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmer la suppression</DialogTitle>
          </DialogHeader>
          <p className="text-muted-foreground">
            Êtes-vous sûr de vouloir supprimer <strong>{deletingMember?.name}</strong> ?
            Cette action est irréversible.
          </p>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={() => setDeletingMember(null)}>
              Annuler
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Supprimer
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
