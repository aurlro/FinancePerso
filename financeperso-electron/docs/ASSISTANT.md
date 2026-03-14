# Page Assistant IA

La page **Assistant IA** fournit une interface conversationnelle pour interagir avec vos données financières de manière naturelle.

## Fonctionnalités

### 💬 Chat Conversationnel
- Interface moderne style ChatGPT/Claude
- Bulles de messages avec distinction user/IA
- Typing indicator animé
- Support du formatage markdown basique (gras, titres)

### 📊 Analyses Financières
L'IA peut répondre aux questions suivantes :
- "Combien ai-je dépensé ce mois-ci ?"
- "Quelles sont mes plus grosses dépenses ?"
- "Donne-moi des conseils d'économie"
- "Explique-moi mon budget"
- "Quelles sont mes catégories de dépenses ?"

### 🏷️ Catégorisation via Chat
Vous pouvez créer des règles de catégorisation directement dans le chat :
```
Categorise 'CARREFOUR' comme Alimentation
```

### 💡 Suggestions Rapides
Boutons d'action rapide en bas du chat :
- 💰 Analyser mes dépenses
- 💡 Trouver des économies  
- 📊 Expliquer mon budget
- 🏷️ Meilleures catégories

### 💾 Historique des Conversations
- Sauvegarde locale dans localStorage
- Liste des conversations passées
- Possibilité de reprendre une conversation
- Suppression de conversations

## Architecture

### Composants Principaux

```tsx
<Assistant>
  <ChatContainer>
    <MessagesList>
      <MessageBubble />     // Bulle de message individuelle
      <TypingIndicator />   // Indicateur "IA en train d'écrire"
    </MessagesList>
    <QuickSuggestions />    // Boutons de suggestions rapides
    <ChatInput />           // Input avec bouton envoi
  </ChatContainer>
  <ConversationsSidebar />  // Historique (desktop)
</Assistant>
```

### Hooks Utilisés

- `useElectron()` - Accès aux données financières (stats, budgets, catégories)
- `useAI()` - Création de règles d'apprentissage
- `useConversations()` - Gestion de l'historique des conversations

### Types

```typescript
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
```

## Intégration

### Navigation
La page est accessible via :
- URL : `/#/assistant`
- Menu de navigation : "Assistant IA" (icône 🤖)

### Dépendances
- React 18+
- Tailwind CSS
- Composants shadcn/ui (Card, Button, Input)
- Hooks internes : useElectron, useAI

## Personnalisation

### Ajouter une Nouvelle Suggestion Rapide

Modifier le tableau `QUICK_SUGGESTIONS` dans `Assistant.tsx` :

```typescript
const QUICK_SUGGESTIONS = [
  // ... suggestions existantes
  { 
    icon: '📈', 
    label: 'Voir les tendances', 
    prompt: 'Montre-moi mes tendances de dépenses sur les 3 derniers mois' 
  },
];
```

### Ajouter un Nouveau Type d'Analyse

Modifier la fonction `analyzeFinances()` dans `Assistant.tsx` :

```typescript
if (lowerQuestion.includes('mes tendances')) {
  // Récupérer les données
  const trends = await getTrends();
  
  // Formater la réponse
  let response = `## 📈 Vos tendances\n\n`;
  // ...
  return response;
}
```

## Tests

Les tests E2E sont dans `tests/e2e/assistant.spec.ts` :

```bash
npm run test:e2e -- assistant.spec.ts
```

## Roadmap Futures Améliorations

- [ ] Intégration avec l'API Gemini/OpenAI pour des réponses plus naturelles
- [ ] Reconnaissance vocale pour l'input
- [ ] Export des conversations en PDF
- [ ] Suggestions contextuelles basées sur l'historique
- [ ] Mode "analyse avancée" avec graphiques
