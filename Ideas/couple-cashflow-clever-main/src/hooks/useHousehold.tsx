import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";

export function useHousehold() {
  const { user } = useAuth();

  const profileQuery = useQuery({
    queryKey: ["profile", user?.id],
    enabled: !!user,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("profiles")
        .select("*, households(*)")
        .eq("id", user!.id)
        .single();
      if (error) throw error;
      return data;
    },
  });

  return profileQuery;
}

export function useHouseholdMembers() {
  const { user } = useAuth();

  return useQuery({
    queryKey: ["household-members", user?.id],
    enabled: !!user,
    queryFn: async () => {
      const { data: profile } = await supabase
        .from("profiles")
        .select("household_id")
        .eq("id", user!.id)
        .single();
      if (!profile?.household_id) return [];

      const { data, error } = await supabase
        .from("household_members")
        .select("*")
        .eq("household_id", profile.household_id)
        .order("is_active", { ascending: false })
        .order("created_at", { ascending: true });
      if (error) throw error;
      return data;
    },
  });
}

export function useUpdateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ displayName }: { displayName: string }) => {
      const { error } = await supabase
        .from("profiles")
        .update({ display_name: displayName })
        .eq("id", (await supabase.auth.getUser()).data.user!.id);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
      qc.invalidateQueries({ queryKey: ["household-members"] });
      toast.success("Profil mis à jour");
    },
    onError: () => toast.error("Erreur lors de la mise à jour"),
  });
}

export function useUpdateHousehold() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ householdId, name }: { householdId: string; name: string }) => {
      const { error } = await supabase
        .from("households")
        .update({ name })
        .eq("id", householdId);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
      toast.success("Nom du foyer mis à jour");
    },
    onError: () => toast.error("Erreur lors de la mise à jour"),
  });
}

export function useInvitations() {
  const { user } = useAuth();

  return useQuery({
    queryKey: ["invitations", user?.id],
    enabled: !!user,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("household_invitations")
        .select("*")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data;
    },
  });
}

export function useSendInvitation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ householdId, email }: { householdId: string; email: string }) => {
      const userId = (await supabase.auth.getUser()).data.user!.id;
      const { error } = await supabase.from("household_invitations").insert({
        household_id: householdId,
        invited_by: userId,
        invited_email: email,
      });
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["invitations"] });
      toast.success("Invitation envoyée");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useAcceptInvitation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (invitationId: string) => {
      const { error } = await supabase.rpc("accept_invitation", {
        invitation_id: invitationId,
      });
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries();
      toast.success("Invitation acceptée ! Vous avez rejoint le foyer.");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useDeleteInvitation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (invitationId: string) => {
      const { error } = await supabase
        .from("household_invitations")
        .delete()
        .eq("id", invitationId);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["invitations"] });
      toast.success("Invitation supprimée");
    },
    onError: () => toast.error("Erreur lors de la suppression"),
  });
}

export function useToggleMemberActive() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, isActive }: { id: string; isActive: boolean }) => {
      const { error } = await supabase
        .from("household_members")
        .update({ is_active: isActive })
        .eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["household-members"] });
      toast.success("Statut du membre mis à jour");
    },
    onError: () => toast.error("Erreur lors de la mise à jour"),
  });
}

/* ─── Update card identifier ────────────────────────── */

export function useUpdateMemberCard() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, cardIdentifier }: { id: string; cardIdentifier: string }) => {
      const { error } = await supabase
        .from("household_members")
        .update({ card_identifier: cardIdentifier })
        .eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["household-members"] });
    },
    onError: () => toast.error("Erreur lors de la mise à jour de la carte"),
  });
}

/* ─── Ghost member CRUD ─────────────────────────────── */

export function useAddGhostMember() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ householdId, displayName, cardIdentifier }: {
      householdId: string;
      displayName: string;
      cardIdentifier?: string;
    }) => {
      const { error } = await supabase.from("household_members").insert({
        household_id: householdId,
        display_name: displayName,
        card_identifier: cardIdentifier?.trim() || null,
        is_active: false,
        user_id: null,
      });
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["household-members"] });
      toast.success("Membre ajouté");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useUpdateGhostMember() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, displayName, cardIdentifier }: {
      id: string;
      displayName: string;
      cardIdentifier?: string;
    }) => {
      const { error } = await supabase.from("household_members").update({
        display_name: displayName,
        card_identifier: cardIdentifier?.trim() || null,
      }).eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["household-members"] });
      toast.success("Membre mis à jour");
    },
    onError: () => toast.error("Erreur lors de la mise à jour"),
  });
}

export function useDeleteGhostMember() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("household_members").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["household-members"] });
      toast.success("Membre supprimé");
    },
    onError: () => toast.error("Erreur lors de la suppression"),
  });
}
