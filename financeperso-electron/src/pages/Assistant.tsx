import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useElectron } from '@/hooks/useElectron';
import { useAI } from '@/hooks/useAI';
import { cn } from '@/lib/utils';
// Simple text formatter (replaces react-markdown for basic formatting)
function formatText(text: string): React.ReactNode {
  const lines = text.split('\n');
  return lines.map((line, index) => {
    // Headers
    if (line.startsWith('## ')) {
      return <h3 key={index} className="text-lg font-bold text-gray-900 mb-2">{line.replace('## ', '')}</h3>;
    }
    // Bold text **text**
    const boldRegex = /\*\*(.+?)\*\*/g;
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    let match;
    
    while ((match = boldRegex.exec(line)) !== null) {
      if (match.index > lastIndex) {
        parts.push(line.slice(lastIndex, match.index));
      }
      parts.push(<strong key={match.index} className="font-semibold text-emerald-700">{match[1]}</strong>);
      lastIndex = match.index + match[0].length;
    }
    if (lastIndex < line.length) {
      parts.push(line.slice(lastIndex));
    }
    
    if (parts.length === 0) parts.push(line);
    
    return <p key={index} className={line.trim() === '' ? 'h-2' : 'mb-1'}>{parts}</p>;
  });
}

// Types pour le chat
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: {
    type?: 'analysis' | 'categorization' | 'advice' | 'general';
    data?: any;
  };
}

interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
}

// Suggestions rapides
const QUICK_SUGGESTIONS = [
  { icon: '💰', label: 'Analyser mes dépenses', prompt: 'Analyse mes dépenses du mois en cours et donne-moi un résumé' },
  { icon: '💡', label: 'Trouver des économies', prompt: 'Où puis-je faire des économies sur mes dépenses ce mois-ci ?' },
  { icon: '📊', label: 'Expliquer mon budget', prompt: 'Explique-moi l\'état de mon budget ce mois-ci' },
  { icon: '🏷️', label: 'Meilleures catégories', prompt: 'Quelles sont mes catégories de dépenses les plus importantes ?' },
];

// Générer un ID unique
const generateId = () => Math.random().toString(36).substring(2, 15);

// Formater la date
const formatTime = (date: Date) => {
  return new Intl.DateTimeFormat('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

// Composant pour le typing indicator
function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-2 bg-gray-100 rounded-2xl rounded-tl-sm w-fit">
      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
    </div>
  );
}

// Composant pour une bulle de message
interface MessageBubbleProps {
  message: ChatMessage;
  isLast: boolean;
}

function MessageBubble({ message, isLast }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (isLast && scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [isLast]);

  return (
    <div
      ref={scrollRef}
      className={cn(
        'flex gap-3 mb-4',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'w-8 h-8 rounded-full flex items-center justify-center text-sm shrink-0',
          isUser
            ? 'bg-emerald-100 text-emerald-700'
            : 'bg-gradient-to-br from-blue-500 to-purple-600 text-white'
        )}
      >
        {isUser ? '👤' : '🤖'}
      </div>

      {/* Message content */}
      <div className={cn('flex flex-col max-w-[80%]', isUser ? 'items-end' : 'items-start')}>
        <div
          className={cn(
            'px-4 py-2.5 rounded-2xl text-sm leading-relaxed',
            isUser
              ? 'bg-emerald-600 text-white rounded-tr-sm'
              : 'bg-gray-100 text-gray-900 rounded-tl-sm'
          )}
        >
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="text-sm leading-relaxed">
              {formatText(message.content)}
            </div>
          )}
        </div>
        <span className="text-xs text-gray-400 mt-1 px-1">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
}

// Composant pour les suggestions rapides
interface QuickSuggestionsProps {
  onSuggestionClick: (prompt: string) => void;
  disabled?: boolean;
}

function QuickSuggestions({ onSuggestionClick, disabled }: QuickSuggestionsProps) {
  return (
    <div className="flex flex-wrap gap-2 px-4 py-3 border-t border-gray-100">
      {QUICK_SUGGESTIONS.map((suggestion) => (
        <Button
          key={suggestion.label}
          variant="outline"
          size="sm"
          disabled={disabled}
          onClick={() => onSuggestionClick(suggestion.prompt)}
          className="text-xs bg-white hover:bg-emerald-50 border-gray-200 hover:border-emerald-200 transition-colors"
        >
          <span className="mr-1.5">{suggestion.icon}</span>
          {suggestion.label}
        </Button>
      ))}
    </div>
  );
}

// Composant pour l'input du chat
interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

function ChatInput({ onSend, disabled, placeholder = 'Posez votre question...' }: ChatInputProps) {
  const [input, setInput] = React.useState('');
  const inputRef = React.useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  // Focus automatique
  React.useEffect(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [disabled]);

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4 border-t border-gray-100 bg-white">
      <Input
        ref={inputRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className="flex-1 bg-gray-50 border-gray-200 focus:bg-white transition-colors"
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
      />
      <Button
        type="submit"
        disabled={disabled || !input.trim()}
        className="bg-emerald-600 hover:bg-emerald-700 px-4"
      >
        {disabled ? (
          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        ) : (
          <>
            <span className="mr-1">📤</span>
            Envoyer
          </>
        )}
      </Button>
    </form>
  );
}

// Hook pour gérer les conversations
function useConversations() {
  const [conversations, setConversations] = React.useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = React.useState<Conversation | null>(null);

  // Charger depuis localStorage au montage
  React.useEffect(() => {
    const saved = localStorage.getItem('financeperso_conversations');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        const restored = parsed.map((c: any) => ({
          ...c,
          createdAt: new Date(c.createdAt),
          updatedAt: new Date(c.updatedAt),
          messages: c.messages.map((m: any) => ({
            ...m,
            timestamp: new Date(m.timestamp),
          })),
        }));
        setConversations(restored);
        if (restored.length > 0) {
          setCurrentConversation(restored[0]);
        }
      } catch (e) {
        console.error('Failed to load conversations:', e);
      }
    }
  }, []);

  // Sauvegarder dans localStorage
  React.useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('financeperso_conversations', JSON.stringify(conversations));
    }
  }, [conversations]);

  const createConversation = () => {
    const newConversation: Conversation = {
      id: generateId(),
      title: 'Nouvelle conversation',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setConversations((prev) => [newConversation, ...prev]);
    setCurrentConversation(newConversation);
    return newConversation;
  };

  const addMessage = (conversationId: string, message: ChatMessage) => {
    setConversations((prev) =>
      prev.map((c) =>
        c.id === conversationId
          ? {
              ...c,
              messages: [...c.messages, message],
              updatedAt: new Date(),
              title:
                c.messages.length === 0 && message.role === 'user'
                  ? message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
                  : c.title,
            }
          : c
      )
    );

    setCurrentConversation((prev) =>
      prev?.id === conversationId
        ? {
            ...prev,
            messages: [...prev.messages, message],
            updatedAt: new Date(),
            title:
              prev.messages.length === 0 && message.role === 'user'
                ? message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
                : prev.title,
          }
        : prev
    );
  };

  const selectConversation = (id: string) => {
    const conv = conversations.find((c) => c.id === id);
    if (conv) {
      setCurrentConversation(conv);
    }
  };

  const deleteConversation = (id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (currentConversation?.id === id) {
      const remaining = conversations.filter((c) => c.id !== id);
      setCurrentConversation(remaining.length > 0 ? remaining[0] : null);
    }
  };

  return {
    conversations,
    currentConversation,
    createConversation,
    addMessage,
    selectConversation,
    deleteConversation,
  };
}

// Fonction pour analyser les transactions et générer une réponse
async function analyzeFinances(
  electron: ReturnType<typeof useElectron>,
  question: string
): Promise<string> {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;

  try {
    // Récupérer les stats du mois
    const stats = await electron.getStatsByMonth(year, month);
    const categories = await electron.getCategoriesStats(year, month);
    const budgets = await electron.getBudgetStatus(year, month);

    const totalIncome = stats.find((s: any) => s.type === 'income')?.total || 0;
    const totalExpense = stats.find((s: any) => s.type === 'expense')?.total || 0;
    const balance = totalIncome - totalExpense;

    // Analyser la question pour donner une réponse appropriée
    const lowerQuestion = question.toLowerCase();

    // Question sur les dépenses du mois
    if (lowerQuestion.includes('dépensé') || lowerQuestion.includes('dépenses du mois')) {
      const topCategories = categories
        .sort((a: any, b: any) => b.total - a.total)
        .slice(0, 5);

      let response = `## 💰 Vos dépenses ce mois-ci\n\n`;
      response += `**Total des dépenses :** ${totalExpense.toFixed(2)}€\n\n`;
      response += `**Top 5 des catégories :**\n`;
      topCategories.forEach((cat: any, index: number) => {
        const percentage = totalExpense > 0 ? (cat.total / totalExpense) * 100 : 0;
        response += `${index + 1}. **${cat.category}** : ${cat.total.toFixed(2)}€ (${percentage.toFixed(1)}%)\n`;
      });
      response += `\n💡 *Vous avez effectué ${categories.reduce((sum: number, c: any) => sum + c.count, 0)} transactions ce mois-ci.*`;
      return response;
    }

    // Question sur les plus grosses dépenses
    if (lowerQuestion.includes('grosses dépenses') || lowerQuestion.includes('plus gros')) {
      const topCategories = categories.sort((a: any, b: any) => b.total - a.total).slice(0, 3);

      let response = `## 🔍 Vos plus grosses dépenses\n\n`;
      topCategories.forEach((cat: any, index: number) => {
        const percentage = totalExpense > 0 ? (cat.total / totalExpense) * 100 : 0;
        response += `${index + 1}. **${cat.category}** : ${cat.total.toFixed(2)}€ (${percentage.toFixed(1)}%)\n`;
      });
      return response;
    }

    // Question sur les économies
    if (lowerQuestion.includes('économies') || lowerQuestion.includes('économiser')) {
      const overspentBudgets = budgets.filter((b: any) => b.status === 'exceeded');
      const warningBudgets = budgets.filter((b: any) => b.status === 'warning');

      let response = `## 💡 Conseils d'économie\n\n`;
      
      if (overspentBudgets.length > 0) {
        response += `⚠️ **Budgets dépassés :**\n`;
        overspentBudgets.forEach((b: any) => {
          response += `- ${b.category} : ${b.spent_amount.toFixed(2)}€ / ${b.amount.toFixed(2)}€\n`;
        });
        response += `\n`;
      }

      if (warningBudgets.length > 0) {
        response += `⚡ **Budgets en alerte :**\n`;
        warningBudgets.forEach((b: any) => {
          response += `- ${b.category} : ${b.percentage.toFixed(0)}% utilisé\n`;
        });
        response += `\n`;
      }

      if (balance > 0) {
        response += `✅ Bonne nouvelle ! Vous avez un **excédent de ${balance.toFixed(2)}€** ce mois-ci.\n`;
        response += `💡 Conseil : Mettez cet excédent de côté dans votre épargne.`;
      } else {
        response += `⚠️ Attention, vous êtes en **déficit de ${Math.abs(balance).toFixed(2)}€**.\n`;
        response += `💡 Conseil : Essayez de réduire les dépenses dans les catégories les plus élevées.`;
      }
      return response;
    }

    // Question sur le budget
    if (lowerQuestion.includes('budget')) {
      const totalBudget = budgets.reduce((sum: number, b: any) => sum + b.amount, 0);
      const exceededCount = budgets.filter((b: any) => b.status === 'exceeded').length;
      const warningCount = budgets.filter((b: any) => b.status === 'warning').length;

      let response = `## 📊 État de votre budget\n\n`;
      response += `**Budget total défini :** ${totalBudget.toFixed(2)}€\n`;
      response += `**Dépenses totales :** ${totalExpense.toFixed(2)}€\n\n`;
      
      if (exceededCount > 0) {
        response += `🔴 **${exceededCount}** budget(s) dépassé(s)\n`;
      }
      if (warningCount > 0) {
        response += `🟡 **${warningCount}** budget(s) en alerte\n`;
      }
      if (exceededCount === 0 && warningCount === 0) {
        response += `🟢 Tous vos budgets sont respectés !\n`;
      }

      return response;
    }

    // Question sur les catégories
    if (lowerQuestion.includes('catégories')) {
      const sortedCategories = categories.sort((a: any, b: any) => b.total - a.total);
      
      let response = `## 🏷️ Vos catégories de dépenses\n\n`;
      sortedCategories.forEach((cat: any, index: number) => {
        const percentage = totalExpense > 0 ? (cat.total / totalExpense) * 100 : 0;
        response += `${index + 1}. **${cat.category}** : ${cat.total.toFixed(2)}€ (${cat.count} transactions, ${percentage.toFixed(1)}%)\n`;
      });
      return response;
    }

    // Analyse générique
    let response = `## 📈 Analyse de vos finances\n\n`;
    response += `**Revenus :** ${totalIncome.toFixed(2)}€\n`;
    response += `**Dépenses :** ${totalExpense.toFixed(2)}€\n`;
    response += `**Solde :** ${balance >= 0 ? '+' : ''}${balance.toFixed(2)}€\n\n`;
    
    if (categories.length > 0) {
      response += `**Principales catégories :**\n`;
      categories
        .sort((a: any, b: any) => b.total - a.total)
        .slice(0, 3)
        .forEach((cat: any) => {
          response += `- ${cat.category} : ${cat.total.toFixed(2)}€\n`;
        });
    }

    return response;
  } catch (error) {
    console.error('Error analyzing finances:', error);
    return `❌ Désolé, je n'ai pas pu analyser vos données financières. Vérifiez que vous avez importé des transactions.`;
  }
}

// Page principale Assistant
export function Assistant() {
  const electron = useElectron();
  const ai = useAI();
  const [isTyping, setIsTyping] = React.useState(false);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const {
    conversations,
    currentConversation,
    createConversation,
    addMessage,
    selectConversation,
    deleteConversation,
  } = useConversations();

  // Créer une conversation initiale si aucune
  React.useEffect(() => {
    if (!currentConversation) {
      createConversation();
    }
  }, []);

  // Scroll automatique vers le bas
  React.useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [currentConversation?.messages, isTyping]);

  // Gérer l'envoi d'un message
  const handleSend = async (content: string) => {
    if (!currentConversation) return;

    // Ajouter le message utilisateur
    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    addMessage(currentConversation.id, userMessage);

    // Vérifier si c'est une demande de catégorisation
    const categorizationMatch = content.match(/categorise?\s+['"]?([^'"]+)['"]?\s+(?:comme?|dans?|en?)\s+(.+)/i);
    if (categorizationMatch) {
      const [, label, category] = categorizationMatch;
      setIsTyping(true);
      
      try {
        // Créer une règle d'apprentissage
        await ai.createRule(label.trim().toUpperCase(), category.trim());
        
        const response: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          content: `✅ J'ai appris que **"${label.trim()}"** correspond à la catégorie **${category.trim()}**.\n\nCette règle sera appliquée automatiquement aux futures transactions.`,
          timestamp: new Date(),
          metadata: { type: 'categorization' },
        };
        addMessage(currentConversation.id, response);
      } catch (error) {
        const response: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          content: `❌ Désolé, je n'ai pas pu créer cette règle. Erreur : ${error instanceof Error ? error.message : 'inconnue'}`,
          timestamp: new Date(),
        };
        addMessage(currentConversation.id, response);
      } finally {
        setIsTyping(false);
      }
      return;
    }

    // Analyser les finances pour les autres questions
    setIsTyping(true);
    
    // Simuler un délai de réflexion de l'IA
    setTimeout(async () => {
      try {
        const analysis = await analyzeFinances(electron, content);
        
        const response: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          content: analysis,
          timestamp: new Date(),
          metadata: { type: 'analysis' },
        };
        addMessage(currentConversation.id, response);
      } catch (error) {
        const response: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          content: `❌ Désolé, une erreur s'est produite lors de l'analyse. Veuillez réessayer.`,
          timestamp: new Date(),
        };
        addMessage(currentConversation.id, response);
      } finally {
        setIsTyping(false);
      }
    }, 800);
  };

  // Gérer le clic sur une suggestion
  const handleSuggestionClick = (prompt: string) => {
    handleSend(prompt);
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex gap-4">
      {/* Sidebar avec l'historique des conversations */}
      <Card className="w-64 hidden lg:flex flex-col">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <span>💬</span>
            Historique
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-auto p-3 pt-0">
          <Button
            onClick={createConversation}
            className="w-full mb-4 bg-emerald-600 hover:bg-emerald-700"
            size="sm"
          >
            <span className="mr-2">+</span>
            Nouvelle conversation
          </Button>

          <div className="space-y-2">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => selectConversation(conv.id)}
                className={cn(
                  'group relative p-3 rounded-lg cursor-pointer text-sm transition-colors',
                  currentConversation?.id === conv.id
                    ? 'bg-emerald-50 text-emerald-900 border border-emerald-200'
                    : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                )}
              >
                <p className="font-medium truncate pr-6">{conv.title}</p>
                <p className="text-xs text-gray-400 mt-1">
                  {conv.messages.length} message{conv.messages.length !== 1 ? 's' : ''}
                </p>
                
                {/* Bouton supprimer */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteConversation(conv.id);
                  }}
                  className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-opacity"
                  title="Supprimer"
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>

          {conversations.length === 0 && (
            <p className="text-sm text-gray-400 text-center py-4">
              Aucune conversation
            </p>
          )}
        </CardContent>
      </Card>

      {/* Zone de chat principale */}
      <Card className="flex-1 flex flex-col">
        <CardHeader className="pb-3 border-b border-gray-100">
          <CardTitle className="text-lg flex items-center gap-2">
            <span className="bg-gradient-to-br from-blue-500 to-purple-600 text-white w-8 h-8 rounded-full flex items-center justify-center text-sm">
              🤖
            </span>
            Assistant IA
            <span className="text-xs font-normal text-gray-400 ml-2">
              Posez-moi vos questions sur vos finances
            </span>
          </CardTitle>
        </CardHeader>

        {/* Messages */}
        <CardContent className="flex-1 overflow-auto p-4 space-y-4">
          {currentConversation?.messages.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-3xl mx-auto mb-4">
                🤖
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Bienvenue sur votre Assistant IA
              </h3>
              <p className="text-gray-500 max-w-md mx-auto mb-6">
                Je peux vous aider à analyser vos finances, trouver des économies, 
                ou même catégoriser vos transactions automatiquement.
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {QUICK_SUGGESTIONS.map((suggestion) => (
                  <Button
                    key={suggestion.label}
                    variant="outline"
                    size="sm"
                    onClick={() => handleSuggestionClick(suggestion.prompt)}
                    className="text-xs"
                  >
                    <span className="mr-1.5">{suggestion.icon}</span>
                    {suggestion.label}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {currentConversation?.messages.map((message, index) => (
            <MessageBubble
              key={message.id}
              message={message}
              isLast={index === currentConversation.messages.length - 1}
            />
          ))}

          {isTyping && (
            <div className="flex gap-3 mb-4">
              <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm bg-gradient-to-br from-blue-500 to-purple-600 text-white shrink-0">
                🤖
              </div>
              <TypingIndicator />
            </div>
          )}

          <div ref={messagesEndRef} />
        </CardContent>

        {/* Suggestions rapides */}
        {currentConversation && currentConversation.messages.length > 0 && (
          <QuickSuggestions
            onSuggestionClick={handleSuggestionClick}
            disabled={isTyping}
          />
        )}

        {/* Input */}
        <ChatInput
          onSend={handleSend}
          disabled={isTyping}
          placeholder="Posez votre question (ex: Combien ai-je dépensé ce mois-ci ?)"
        />
      </Card>
    </div>
  );
}

export default Assistant;
