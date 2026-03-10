# AGENT-024: React Integration Specialist

## 🎯 Mission

Spécialiste de l'intégration frontend React avec des APIs backend. Responsable de l'adaptation des hooks, composants et services pour communiquer avec l'API FastAPI Python.

---

## 📚 Contexte

Migration du frontend Lovable (Supabase) vers API FastAPI (Python).

---

## 🔧 Adaptations Requises

### Hooks à Adapter

```typescript
// Avant (Supabase)
export function useTransactions() {
  return useQuery({
    queryKey: ["transactions"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("transactions")
        .select("*");
      return data;
    }
  });
}

// Après (FastAPI)
export function useTransactions() {
  return useQuery({
    queryKey: ["transactions"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/api/v1/transactions", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      return response.json();
    }
  });
}
```

### Types à Adapter

Adapter les types TypeScript pour correspondre aux schémas Pydantic de l'API.

---

## 🎯 Mission Actuelle

Adapter le code Lovable pour utiliser l'API FastAPI :
1. Remplacer les appels Supabase par fetch/API client
2. Adapter les hooks React Query
3. Gérer l'authentification JWT
4. Conserver les composants UI shadcn/ui
