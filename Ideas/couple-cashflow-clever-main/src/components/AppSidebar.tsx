import {
  LayoutDashboard,
  ArrowLeftRight,
  Upload,
  Landmark,
  Settings,
  FileText,
  Wallet,
  LogOut,
  BarChart3,
  CalendarCheck,
  Scale,
  RefreshCw,
} from "lucide-react";
import { useLocation, Link } from "react-router-dom";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { ThemeToggle } from "@/components/ThemeToggle";
import { NotificationBell } from "@/components/NotificationBell";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";

const navItems = [
  { title: "Dashboard", icon: LayoutDashboard, path: "/" },
  { title: "Transactions", icon: ArrowLeftRight, path: "/transactions" },
  { title: "Import", icon: Upload, path: "/import" },
  { title: "Comptes", icon: Landmark, path: "/accounts" },
  { title: "Règles", icon: FileText, path: "/rules" },
  { title: "Analytics", icon: BarChart3, path: "/analytics" },
  { title: "Bilan mensuel", icon: CalendarCheck, path: "/recap" },
  { title: "Équilibre", icon: Scale, path: "/balance" },
  { title: "Abonnements", icon: RefreshCw, path: "/subscriptions" },
  { title: "Paramètres", icon: Settings, path: "/settings" },
];

export function AppSidebar() {
  const location = useLocation();
  const { user, signOut } = useAuth();

  return (
    <Sidebar>
      <SidebarHeader className="p-4">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Wallet className="h-4 w-4 text-primary-foreground" />
          </div>
          <span className="text-lg font-semibold tracking-tight">FinCouple</span>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => (
                <SidebarMenuItem key={item.path}>
                  <SidebarMenuButton
                    asChild
                    isActive={location.pathname === item.path}
                    tooltip={item.title}
                  >
                    <Link to={item.path}>
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="p-4 space-y-3">
        {user && (
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground truncate max-w-[140px]">
              {user.email}
            </span>
            <div className="flex items-center gap-1">
              <NotificationBell />
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={signOut}>
                <LogOut className="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>
        )}
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">v1.0</span>
          <ThemeToggle />
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
