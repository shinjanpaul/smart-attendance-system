import React from 'react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  onProfileClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle = 'Supabase Connected' }) => {
  return (
    <header className="fixed top-0 w-full z-50 pt-safe bg-surface/85 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)]">
      <div className="h-16 px-gutter-mobile flex items-center justify-between gap-space-sm">
        <div className="flex items-center gap-space-sm min-w-0">
          <div className="w-8 h-8 rounded-lg bg-primary-fixed flex items-center justify-center text-primary font-bold text-sm shadow-inner shrink-0">
            VF
          </div>
          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-space-xs">
              <span className="font-title-md text-title-md text-on-surface truncate font-semibold">VeriFace</span>
              <span className="px-1.5 py-0.5 rounded-full bg-primary-fixed text-on-primary-fixed-variant font-label-sm text-label-sm tracking-wider uppercase font-semibold">
                AI
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" aria-hidden="true"></span>
              <span className="font-label-sm text-label-sm text-on-surface-variant truncate">
                API Live • 127.0.0.1:8000
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-space-sm shrink-0">
          <div className="hidden sm:flex flex-col items-end">
            <span className="font-label-sm text-label-sm font-semibold text-on-surface">{title}</span>
            <span className="font-label-sm text-label-sm text-primary">{subtitle}</span>
          </div>
          <div className="relative w-11 h-11 flex items-center justify-center">
            <div className="w-8 h-8 rounded-full bg-surface-container-high ring-2 ring-primary/20 flex items-center justify-center text-primary font-semibold text-xs">
              PS
            </div>
            <span className="absolute bottom-1 right-1 w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-surface" title="System Online"></span>
          </div>
        </div>
      </div>
    </header>
  );
};
