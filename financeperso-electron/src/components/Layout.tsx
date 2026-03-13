import * as React from 'react';
import { Navigation } from './Navigation';
import { ErrorBoundary } from './ui/ErrorState';
import { CommandPalette, CommandPaletteTrigger, CommandPaletteTriggerMobile } from './CommandPalette';
import { cn } from '@/lib/utils';
import { Menu, X } from 'lucide-react';
import { Button } from './ui/button';

interface LayoutProps {
  children: React.ReactNode;
  className?: string;
}

// Mobile navigation hook
function useMobileMenu() {
  const [isOpen, setIsOpen] = React.useState(false);
  const [isMobile, setIsMobile] = React.useState(false);

  React.useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth >= 768) {
        setIsOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return { isOpen, setIsOpen, isMobile };
}

// Sidebar component for desktop
function Sidebar({ 
  className, 
  onSearchClick 
}: { 
  className?: string;
  onSearchClick: () => void;
}) {
  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen w-64 border-r bg-white hidden md:block",
        className
      )}
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center border-b px-6">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-emerald-500 flex items-center justify-center">
              <span className="text-white font-bold text-lg">F</span>
            </div>
            <span className="text-lg font-semibold text-gray-900">
              FinancePerso
            </span>
          </div>
        </div>
        
        {/* Search Button */}
        <div className="px-4 py-3 border-b border-gray-100">
          <CommandPaletteTrigger onClick={onSearchClick} />
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-auto py-4">
          <Navigation orientation="vertical" />
        </div>

        {/* Footer */}
        <div className="border-t p-4">
          <p className="text-xs text-muted-foreground text-center">
            v5.6.0 · Electron
          </p>
        </div>
      </div>
    </aside>
  );
}

// Mobile header with hamburger menu
function MobileHeader({
  onMenuToggle,
  isOpen,
  onSearchClick,
}: {
  onMenuToggle: () => void;
  isOpen: boolean;
  onSearchClick: () => void;
}) {
  return (
    <header className="fixed top-0 left-0 right-0 z-30 h-16 border-b bg-white md:hidden">
      <div className="flex h-full items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-emerald-500 flex items-center justify-center">
            <span className="text-white font-bold text-lg">F</span>
          </div>
          <span className="text-lg font-semibold text-gray-900">
            FinancePerso
          </span>
        </div>
        <div className="flex items-center gap-1">
          <CommandPaletteTriggerMobile onClick={onSearchClick} />
          <Button
            variant="ghost"
            size="icon"
            onClick={onMenuToggle}
            aria-label={isOpen ? "Fermer le menu" : "Ouvrir le menu"}
          >
            {isOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </Button>
        </div>
      </div>
    </header>
  );
}

// Mobile navigation drawer
function MobileDrawer({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-40 bg-black/50 md:hidden"
        onClick={onClose}
      />
      {/* Drawer */}
      <div className="fixed left-0 top-16 z-50 h-[calc(100vh-4rem)] w-64 border-r bg-white md:hidden">
        <div className="flex h-full flex-col">
          <div className="flex-1 overflow-auto py-4">
            <Navigation orientation="vertical" onItemClick={onClose} />
          </div>
        </div>
      </div>
    </>
  );
}

// Bottom navigation for mobile
function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-30 border-t bg-white md:hidden safe-area-pb">
      <Navigation orientation="horizontal" />
    </nav>
  );
}

export function Layout({ children, className }: LayoutProps) {
  const { isOpen, setIsOpen, isMobile } = useMobileMenu();
  const [commandPaletteOpen, setCommandPaletteOpen] = React.useState(false);

  // Keyboard shortcut to open command palette
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        {/* Command Palette */}
        <CommandPalette open={commandPaletteOpen} onOpenChange={setCommandPaletteOpen} />
        
        {/* Desktop Sidebar */}
        <Sidebar onSearchClick={() => setCommandPaletteOpen(true)} />

        {/* Mobile Header */}
        <MobileHeader
          onMenuToggle={() => setIsOpen(!isOpen)}
          isOpen={isOpen}
          onSearchClick={() => setCommandPaletteOpen(true)}
        />

        {/* Mobile Drawer */}
        <MobileDrawer isOpen={isOpen} onClose={() => setIsOpen(false)} />

        {/* Main Content */}
        <main
          className={cn(
            "min-h-screen transition-all",
            // Mobile: padding for header and bottom nav
            "pt-16 pb-20 px-4",
            // Desktop: padding for sidebar
            "md:ml-64 md:pt-6 md:pb-6 md:px-6",
            className
          )}
        >
          <div className="mx-auto max-w-7xl">
            {children}
          </div>
        </main>

        {/* Mobile Bottom Navigation */}
        <BottomNav />
      </div>
    </ErrorBoundary>
  );
}

// Simple layout without sidebar (for auth pages, etc.)
export function SimpleLayout({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <ErrorBoundary>
      <div className={cn("min-h-screen bg-gray-50", className)}>
        <main className="flex min-h-screen items-center justify-center p-4">
          {children}
        </main>
      </div>
    </ErrorBoundary>
  );
}
