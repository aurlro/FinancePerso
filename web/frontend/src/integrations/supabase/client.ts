// Stub temporaire pour Supabase - à remplacer par l'API FastAPI
// Ce fichier existe juste pour éviter les erreurs de build pendant la migration

export const supabase = {
  from: () => ({
    select: () => ({ data: null, error: null }),
    insert: () => ({ data: null, error: null }),
    update: () => ({ data: null, error: null }),
    delete: () => ({ data: null, error: null }),
  }),
  auth: {
    getSession: () => Promise.resolve({ data: { session: null }, error: null }),
    onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } }),
    signInWithPassword: () => Promise.resolve({ data: null, error: null }),
    signUp: () => Promise.resolve({ data: null, error: null }),
    signOut: () => Promise.resolve({ error: null }),
  },
  functions: {
    invoke: () => Promise.resolve({ data: null, error: null }),
  },
  channel: () => ({
    on: () => ({ subscribe: () => {} }),
    subscribe: () => {},
  }),
  removeChannel: () => {},
};

export type User = any;
export type Session = any;
