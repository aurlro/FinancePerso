/**
 * Hooks React Query pour les Notifications (PR #6)
 * Remplacent les hooks Supabase par des appels API FastAPI + WebSocket
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { notificationsApi, type Notification } from "@/lib/api";

// Hook pour récupérer les notifications
export function useNotifications(unreadOnly: boolean = false) {
  return useQuery({
    queryKey: ["notifications", { unreadOnly }],
    queryFn: () => notificationsApi.list({ unreadOnly }),
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000, // Refetch toutes les minutes
  });
}

// Hook pour le nombre de notifications non lues
export function useUnreadNotificationsCount() {
  return useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: () => notificationsApi.getUnreadCount(),
    staleTime: 10 * 1000,
    refetchInterval: 30 * 1000,
  });
}

// Hook pour marquer une notification comme lue
export function useMarkNotificationAsRead() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => notificationsApi.markAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}

// Hook pour marquer toutes les notifications comme lues
export function useMarkAllNotificationsAsRead() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => notificationsApi.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}

// Hook pour supprimer une notification
export function useDeleteNotification() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => notificationsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}

// Hook WebSocket pour les notifications temps réel
export function useNotificationsWebSocket(enabled: boolean = true) {
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);

  useEffect(() => {
    if (!enabled) return;

    // Note: Le WebSocket nécessite une authentification
    // Pour l'instant, on utilise le polling comme fallback
    const wsUrl = import.meta.env.VITE_WS_URL || "ws://localhost:8000/api/notifications/ws";
    
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        // Envoyer le token d'authentification
        const token = localStorage.getItem("auth_token");
        const userId = localStorage.getItem("user_id");
        if (token && userId) {
          ws.send(JSON.stringify({ token, user_id: parseInt(userId) }));
        }
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setLastMessage(data);
        
        if (data.type === "new_notification") {
          // Invalider le cache pour recharger les notifications
          queryClient.invalidateQueries({ queryKey: ["notifications"] });
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setIsConnected(false);
      };

      return () => {
        ws.close();
      };
    } catch (error) {
      console.error("Failed to connect WebSocket:", error);
    }
  }, [enabled, queryClient]);

  return { isConnected, lastMessage, ws: wsRef.current };
}
