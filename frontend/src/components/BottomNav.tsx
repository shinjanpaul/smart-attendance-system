import React from 'react';

export type NavTab = 'dashboard' | 'take-attendance' | 'attendance-review' | 'history' | 'face-id';

interface BottomNavProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({ currentTab, onSelectTab }) => {
  return (
    <nav
      className="fixed bottom-0 w-full z-50 pb-safe bg-surface/90 backdrop-blur-xl shadow-[0_-2px_12px_rgba(0,0,0,0.04)]"
      aria-label="Bottom App Navigation"
    >
      <div className="flex items-center justify-around h-16 px-gutter-mobile">
        {/* Dashboard */}
        <button
          type="button"
          onClick={() => onSelectTab('dashboard')}
          aria-current={currentTab === 'dashboard' ? 'page' : undefined}
          className={`flex flex-col items-center justify-center min-w-[48px] min-h-[48px] gap-0.5 transition-colors ${
            currentTab === 'dashboard' ? 'text-primary font-semibold' : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[22px]">dashboard</span>
          <span className="font-label-sm text-label-sm text-xs">Dashboard</span>
        </button>

        {/* Scan (Hero action) */}
        <button
          type="button"
          onClick={() => onSelectTab('take-attendance')}
          aria-current={currentTab === 'take-attendance' ? 'page' : undefined}
          className="relative -top-2 flex flex-col items-center justify-center min-w-[52px] min-h-[52px] text-on-primary group"
          aria-label="Scan Classroom Photos"
        >
          <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center shadow-lg shadow-primary/30 transition-transform group-active:scale-95 group-hover:scale-105">
            <span className="material-symbols-outlined text-[24px]">center_focus_strong</span>
          </div>
          <span
            className={`font-label-sm text-label-sm text-xs mt-1 font-semibold ${
              currentTab === 'take-attendance' ? 'text-primary' : 'text-on-surface-variant'
            }`}
          >
            Scan
          </span>
        </button>

        {/* Review */}
        <button
          type="button"
          onClick={() => onSelectTab('attendance-review')}
          aria-current={currentTab === 'attendance-review' ? 'page' : undefined}
          className={`flex flex-col items-center justify-center min-w-[48px] min-h-[48px] gap-0.5 transition-colors ${
            currentTab === 'attendance-review' ? 'text-primary font-semibold' : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[22px]">fact_check</span>
          <span className="font-label-sm text-label-sm text-xs">Review</span>
        </button>

        {/* History */}
        <button
          type="button"
          onClick={() => onSelectTab('history')}
          aria-current={currentTab === 'history' ? 'page' : undefined}
          className={`flex flex-col items-center justify-center min-w-[48px] min-h-[48px] gap-0.5 transition-colors ${
            currentTab === 'history' ? 'text-primary font-semibold' : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[22px]">history</span>
          <span className="font-label-sm text-label-sm text-xs">History</span>
        </button>

        {/* Face ID */}
        <button
          type="button"
          onClick={() => onSelectTab('face-id')}
          aria-current={currentTab === 'face-id' ? 'page' : undefined}
          className={`flex flex-col items-center justify-center min-w-[48px] min-h-[48px] gap-0.5 transition-colors ${
            currentTab === 'face-id' ? 'text-primary font-semibold' : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[22px]">person_search</span>
          <span className="font-label-sm text-label-sm text-xs">Face ID</span>
        </button>
      </div>
    </nav>
  );
};
