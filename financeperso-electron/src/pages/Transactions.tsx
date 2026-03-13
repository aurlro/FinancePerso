import * as React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useTransactions } from '@/hooks/useTransactions';
import { useMembers, useSplitTransaction } from '@/hooks/useMembers';
import { Member } from '@/types';
import { User } from 'lucide-react';
import { cn } from '@/lib/utils';

declare global {
  interface Window {
    electronAPI: {
      getAllTransactions: (limit?: number, offset?: number) => Promise<any[]>;
      createTransaction: (data: any) => Promise<any>;
      deleteTransaction: (id: number) => Promise<any>;
      getCategories: () => Promise<any[]>;
    };
  }
}

function MemberBadge({ member, size = 'sm' }: { member?: Member | null; size?: 'sm' | 'md' }) {
  if (!member) {
    return (
      <div className={cn(
        'rounded-full flex items-center justify-center bg-gray-100 text-gray-400',
        size === 'sm' ? 'w-6 h-6 text-xs' : 'w-8 h-8 text-sm'
      )}>
        <User className="w-3 h-3" />
      </div>
    );
  }

  return (
    <div
      className={cn(
        'rounded-full flex items-center justify-center border-2',
        size === 'sm' ? 'w-6 h-6 text-xs' : 'w-8 h-8 text-sm'
      )}
      style={{ 
        backgroundColor: `${member.color}20`,
        borderColor: member.color 
      }}
      title={member.name}
    >
      <span>{member.emoji}</span>
    </div>
  );
}

function MemberSelect({ 
  transactionId, 
  currentMemberId, 
  members, 
  onAssign 
}: { 
  transactionId: number; 
  currentMemberId?: number | null; 
  members: Member[];
  onAssign: (transactionId: number, memberId: number) => void;
}) {
  const currentMember = members.find(m => m.id === currentMemberId);

  return (
    <Select
      value={currentMemberId?.toString() || ''}
      onValueChange={(value) => onAssign(transactionId, parseInt(value))}
    >
      <SelectTrigger className="w-32 h-8 text-xs">
        <div className="flex items-center gap-2">
          <MemberBadge member={currentMember} size="sm" />
          <span className="truncate">{currentMember?.name || 'Assigner...'}</span>
        </div>
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-gray-400" />
            <span>Non assigné</span>
          </div>
        </SelectItem>
        {members.map((member) => (
          <SelectItem key={member.id} value={member.id.toString()}>
            <div className="flex items-center gap-2">
              <span>{member.emoji}</span>
              <span>{member.name}</span>
              {member.type === 'primary' && (
                <span className="text-xs text-emerald-600">(principal)</span>
              )}
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

export function Transactions() {
  const [transactions, setTransactions] = React.useState<any[]>([]);
  const [categories, setCategories] = React.useState<any[]>([]);
  const [transactionMembers, setTransactionMembers] = React.useState<Record<number, Member>>({});
  const [loading, setLoading] = React.useState(true);
  
  const { members, loading: membersLoading } = useMembers();
  const { assignToMember, getMemberForTransaction } = useSplitTransaction();

  React.useEffect(() => {
    loadData();
  }, []);

  // Charger les membres assignés pour chaque transaction
  React.useEffect(() => {
    if (transactions.length > 0 && members.length > 0) {
      loadTransactionMembers();
    }
  }, [transactions, members]);

  const loadTransactionMembers = async () => {
    const memberMap: Record<number, Member> = {};
    for (const tx of transactions) {
      const member = await getMemberForTransaction(tx.id);
      if (member) {
        memberMap[tx.id] = member;
      }
    }
    setTransactionMembers(memberMap);
  };

  const loadData = async () => {
    try {
      setLoading(true);
      const [txData, catData] = await Promise.all([
        window.electronAPI.getAllTransactions(50, 0),
        window.electronAPI.getCategories(),
      ]);
      setTransactions(txData);
      setCategories(catData);
    } catch (error) {
      console.error('Failed to load transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Supprimer cette transaction ?')) return;
    try {
      await window.electronAPI.deleteTransaction(id);
      loadData();
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  const handleAddTest = async () => {
    try {
      const types = ['expense', 'income'];
      const type = types[Math.floor(Math.random() * types.length)];
      const amount = Math.round(Math.random() * 200);
      
      await window.electronAPI.createTransaction({
        date: new Date().toISOString().split('T')[0],
        description: type === 'income' ? 'Salaire' : 'Achat ' + Math.floor(Math.random() * 100),
        amount: amount,
        category: categories[Math.floor(Math.random() * categories.length)]?.name || 'Autre',
        type: type,
        account: 'Compte principal',
        notes: '',
      });
      loadData();
    } catch (error) {
      console.error('Failed to create:', error);
    }
  };

  const handleAssignMember = async (transactionId: number, memberId: number) => {
    const success = await assignToMember(transactionId, memberId);
    if (success) {
      // Mettre à jour le mapping local
      const member = members.find(m => m.id === memberId);
      if (member) {
        setTransactionMembers(prev => ({
          ...prev,
          [transactionId]: member
        }));
      }
    }
  };

  if (loading) {
    return <div className="text-center p-8">Chargement...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">
            Transactions ({transactions.length})
          </h2>
          <p className="text-sm text-muted-foreground">
            Gérez vos transactions et assignez-les aux membres
          </p>
        </div>
        <Button onClick={handleAddTest}>
          ➕ Ajouter test
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="divide-y">
            {transactions.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                Aucune transaction
              </div>
            ) : (
              transactions.map((tx) => {
                const member = transactionMembers[tx.id];
                return (
                  <div
                    key={tx.id}
                    className={cn(
                      'flex items-center justify-between p-4 hover:bg-gray-50 transition-colors',
                      member && 'bg-gray-50/50'
                    )}
                  >
                    <div className="flex items-center gap-4 flex-1 min-w-0">
                      <MemberBadge member={member} size="md" />
                      <div className="flex-1 min-w-0">
                        <div className="font-medium truncate">{tx.description}</div>
                        <div className="text-sm text-muted-foreground">
                          {tx.date} • {tx.category} • {tx.account}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {!membersLoading && (
                        <MemberSelect
                          transactionId={tx.id}
                          currentMemberId={member?.id}
                          members={members}
                          onAssign={handleAssignMember}
                        />
                      )}
                      <span className={`font-bold min-w-[80px] text-right ${tx.type === 'expense' ? 'text-red-600' : 'text-green-600'}`}>
                        {tx.type === 'expense' ? '-' : '+'}{tx.amount.toFixed(2)}€
                      </span>
                      <button
                        onClick={() => handleDelete(tx.id)}
                        className="text-red-500 hover:text-red-700 text-sm"
                      >
                        Supprimer
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
