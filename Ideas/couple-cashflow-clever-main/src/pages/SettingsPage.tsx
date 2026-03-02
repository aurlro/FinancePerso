import { useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  User, Home, Tag, Send, Trash2, Check, X, Plus, Pencil,
  Users, Clock, Mail,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import {
  useHousehold, useHouseholdMembers, useUpdateProfile, useUpdateHousehold,
  useInvitations, useSendInvitation, useDeleteInvitation, useAcceptInvitation,
} from "@/hooks/useHousehold";
import { useCategories } from "@/hooks/useCategories";
import { useCreateCategory, useUpdateCategory, useDeleteCategory } from "@/hooks/useCategoryManagement";

const COLORS = [
  "#ef4444", "#f97316", "#eab308", "#22c55e", "#06b6d4",
  "#3b82f6", "#8b5cf6", "#ec4899", "#6b7280", "#14b8a6",
];

export default function SettingsPage() {
  return (
    <AppLayout title="Paramètres">
      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile"><User className="h-4 w-4 mr-1.5" />Profil</TabsTrigger>
          <TabsTrigger value="household"><Home className="h-4 w-4 mr-1.5" />Foyer</TabsTrigger>
          <TabsTrigger value="categories"><Tag className="h-4 w-4 mr-1.5" />Catégories</TabsTrigger>
        </TabsList>

        <TabsContent value="profile"><ProfileTab /></TabsContent>
        <TabsContent value="household"><HouseholdTab /></TabsContent>
        <TabsContent value="categories"><CategoriesTab /></TabsContent>
      </Tabs>
    </AppLayout>
  );
}

/* ─── Profile ───────────────────────────────────────── */
function ProfileTab() {
  const { user } = useAuth();
  const { data: profile, isLoading } = useHousehold();
  const updateProfile = useUpdateProfile();
  const [name, setName] = useState("");
  const [initialized, setInitialized] = useState(false);

  if (isLoading) return <Skeleton className="h-40 w-full" />;

  if (profile && !initialized) {
    setName(profile.display_name || "");
    setInitialized(true);
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Mon profil</CardTitle>
        <CardDescription>{user?.email}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="displayName">Nom d'affichage</Label>
          <div className="flex gap-2">
            <Input
              id="displayName"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Votre prénom"
            />
            <Button
              onClick={() => updateProfile.mutate({ displayName: name })}
              disabled={updateProfile.isPending}
            >
              Enregistrer
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/* ─── Household ─────────────────────────────────────── */
function HouseholdTab() {
  const { data: profile, isLoading } = useHousehold();
  const { data: members } = useHouseholdMembers();
  const { data: invitations } = useInvitations();
  const updateHousehold = useUpdateHousehold();
  const sendInvitation = useSendInvitation();
  const deleteInvitation = useDeleteInvitation();
  const acceptInvitation = useAcceptInvitation();
  const { user } = useAuth();

  const [householdName, setHouseholdName] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [initialized, setInitialized] = useState(false);

  if (isLoading) return <Skeleton className="h-60 w-full" />;

  const household = profile?.households as any;
  if (household && !initialized) {
    setHouseholdName(household.name || "");
    setInitialized(true);
  }

  // Pending invitations where current user is the invitee
  const myPendingInvites = invitations?.filter(
    (i: any) => i.invited_email === user?.email && i.status === "pending"
  ) || [];

  // Invitations sent by this household
  const sentInvites = invitations?.filter(
    (i: any) => i.household_id === household?.id
  ) || [];

  return (
    <div className="space-y-6">
      {/* Accept pending invitations */}
      {myPendingInvites.length > 0 && (
        <Card className="border-primary">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Mail className="h-4 w-4" /> Invitations reçues
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {myPendingInvites.map((inv: any) => (
              <div key={inv.id} className="flex items-center justify-between p-3 rounded-lg border bg-muted/50">
                <span className="text-sm">Vous avez été invité(e) à rejoindre un foyer</span>
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => acceptInvitation.mutate(inv.id)}>
                    <Check className="h-3.5 w-3.5 mr-1" /> Accepter
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Household name */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Nom du foyer</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              value={householdName}
              onChange={(e) => setHouseholdName(e.target.value)}
              placeholder="Nom du foyer"
            />
            <Button
              onClick={() => household && updateHousehold.mutate({ householdId: household.id, name: householdName })}
              disabled={updateHousehold.isPending}
            >
              Enregistrer
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Members */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Users className="h-4 w-4" /> Membres ({members?.length || 0})
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {members?.map((m: any) => (
            <div key={m.id} className="flex items-center justify-between p-3 rounded-lg border">
              <div>
                <p className="text-sm font-medium">{m.display_name || "Sans nom"}</p>
                <p className="text-xs text-muted-foreground">{m.role}</p>
              </div>
              {m.id === user?.id && <Badge variant="secondary">Vous</Badge>}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Invite */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Inviter un partenaire</CardTitle>
          <CardDescription>
            Envoyez une invitation par email. Votre partenaire devra créer un compte puis accepter l'invitation.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              type="email"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              placeholder="email@exemple.com"
            />
            <Button
              onClick={() => {
                if (household && inviteEmail) {
                  sendInvitation.mutate({ householdId: household.id, email: inviteEmail });
                  setInviteEmail("");
                }
              }}
              disabled={sendInvitation.isPending || !inviteEmail}
            >
              <Send className="h-4 w-4 mr-1" /> Inviter
            </Button>
          </div>

          {sentInvites.length > 0 && (
            <>
              <Separator />
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Invitations envoyées</p>
                {sentInvites.map((inv: any) => (
                  <div key={inv.id} className="flex items-center justify-between p-2 rounded border text-sm">
                    <div className="flex items-center gap-2">
                      <Mail className="h-3.5 w-3.5 text-muted-foreground" />
                      <span>{inv.invited_email}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={inv.status === "pending" ? "outline" : inv.status === "accepted" ? "default" : "secondary"}>
                        {inv.status === "pending" ? "En attente" : inv.status === "accepted" ? "Acceptée" : inv.status}
                      </Badge>
                      {inv.status === "pending" && (
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => deleteInvitation.mutate(inv.id)}>
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/* ─── Categories ────────────────────────────────────── */
function CategoriesTab() {
  const { data: categories, isLoading } = useCategories();
  const { data: profile } = useHousehold();
  const createCategory = useCreateCategory();
  const updateCategory = useUpdateCategory();
  const deleteCategory = useDeleteCategory();

  const [newName, setNewName] = useState("");
  const [newColor, setNewColor] = useState(COLORS[0]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const [editColor, setEditColor] = useState("");

  const household = profile?.households as any;

  if (isLoading) return <Skeleton className="h-40 w-full" />;

  const defaultCats = categories?.filter((c) => c.is_default) || [];
  const customCats = categories?.filter((c) => !c.is_default) || [];

  return (
    <div className="space-y-6">
      {/* Add category */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Ajouter une catégorie</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Nom de la catégorie"
            />
            <Button
              onClick={() => {
                if (household && newName.trim()) {
                  createCategory.mutate({ name: newName.trim(), color: newColor, householdId: household.id });
                  setNewName("");
                }
              }}
              disabled={createCategory.isPending || !newName.trim()}
            >
              <Plus className="h-4 w-4 mr-1" /> Ajouter
            </Button>
          </div>
          <div className="flex gap-1.5">
            {COLORS.map((c) => (
              <button
                key={c}
                onClick={() => setNewColor(c)}
                className="h-7 w-7 rounded-full border-2 transition-transform hover:scale-110"
                style={{
                  backgroundColor: c,
                  borderColor: newColor === c ? "hsl(var(--foreground))" : "transparent",
                }}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Custom categories */}
      {customCats.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Catégories personnalisées ({customCats.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {customCats.map((cat) => (
              <div key={cat.id} className="flex items-center justify-between p-3 rounded-lg border">
                {editingId === cat.id ? (
                  <div className="flex items-center gap-2 flex-1">
                    <Input
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      className="h-8"
                    />
                    <div className="flex gap-1">
                      {COLORS.map((c) => (
                        <button
                          key={c}
                          onClick={() => setEditColor(c)}
                          className="h-5 w-5 rounded-full border"
                          style={{
                            backgroundColor: c,
                            borderColor: editColor === c ? "hsl(var(--foreground))" : "transparent",
                          }}
                        />
                      ))}
                    </div>
                    <Button
                      size="sm"
                      onClick={() => {
                        updateCategory.mutate({ id: cat.id, name: editName, color: editColor });
                        setEditingId(null);
                      }}
                    >
                      <Check className="h-3.5 w-3.5" />
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => setEditingId(null)}>
                      <X className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center gap-3">
                      <div className="h-4 w-4 rounded-full" style={{ backgroundColor: cat.color || "#6b7280" }} />
                      <span className="text-sm font-medium">{cat.name}</span>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        onClick={() => {
                          setEditingId(cat.id);
                          setEditName(cat.name);
                          setEditColor(cat.color || COLORS[0]);
                        }}
                      >
                        <Pencil className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-destructive"
                        onClick={() => deleteCategory.mutate(cat.id)}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Default categories */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Catégories par défaut ({defaultCats.length})</CardTitle>
          <CardDescription>Ces catégories sont communes à tous les foyers et ne peuvent pas être supprimées.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {defaultCats.map((cat) => (
              <Badge key={cat.id} variant="secondary" className="gap-1.5">
                <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: cat.color || "#6b7280" }} />
                {cat.name}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
