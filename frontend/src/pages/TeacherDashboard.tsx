import React from 'react';

interface TeacherDashboardProps {
  onStartScan: () => void;
  onNavigateTab: (tab: any) => void;
}

export const TeacherDashboard: React.FC<TeacherDashboardProps> = ({ onStartScan, onNavigateTab }) => {
  return (
    <main className="flex flex-col relative w-full pt-16 pb-28 bg-surface min-h-screen">
      <div className="flex flex-col w-full max-w-lg mx-auto px-4 space-y-space-md">
        {/* Faculty Profile Card */}
        <div className="flex items-center justify-between p-space-md rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/30 mt-space-sm">
          <div className="flex items-center gap-space-sm">
            <div className="relative w-12 h-12 rounded-full overflow-hidden bg-surface-container shrink-0 ring-2 ring-primary/20">
              <img
                src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80"
                alt="Faculty portrait"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex flex-col min-w-0">
              <span className="font-label-sm text-label-sm text-secondary uppercase tracking-wider text-[11px] font-semibold">
                Faculty Portal
              </span>
              <h2 className="font-title-md text-title-md text-on-surface font-bold text-sm">
                Prof. R. Sharma
              </h2>
              <span className="font-body-sm text-body-sm text-on-surface-variant text-xs">
                Dept. of Information Technology
              </span>
            </div>
          </div>

          <div className="flex flex-col items-end text-xs">
            <span className="font-semibold text-primary">Fall 2026</span>
            <span className="text-secondary">Period 04</span>
          </div>
        </div>

        {/* Active Academic Scope */}
        <div className="flex flex-col p-space-md rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/30 space-y-space-xs">
          <div className="flex items-center justify-between text-xs">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-semibold">
              Active Academic Scope
            </span>
            <span className="font-label-sm text-label-sm text-primary font-semibold">Classroom 302</span>
          </div>

          <div className="flex flex-col gap-2 pt-1 text-xs">
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-surface-container-low border border-outline-variant/20">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[18px]">school</span>
                <div>
                  <div className="text-[10px] text-secondary">Assigned Cohort</div>
                  <div className="font-semibold text-on-surface">B.Tech IT - 4th Year - Sec A</div>
                </div>
              </div>
              <span className="material-symbols-outlined text-secondary text-[18px]">expand_more</span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-xl bg-surface-container-low border border-outline-variant/20">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[18px]">dns</span>
                <div>
                  <div className="text-[10px] text-secondary">Course Module</div>
                  <div className="font-semibold text-on-surface">Distributed Operating Systems (IT801)</div>
                </div>
              </div>
              <span className="material-symbols-outlined text-secondary text-[18px]">expand_more</span>
            </div>
          </div>
        </div>

        {/* Stats Bento Grid */}
        <div className="grid grid-cols-3 gap-2">
          {/* Enrolled */}
          <div className="flex flex-col p-3 rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/30 text-center">
            <div className="flex items-center justify-center text-primary mb-1">
              <span className="material-symbols-outlined text-[20px]">groups</span>
            </div>
            <span className="font-headline-sm text-headline-sm font-bold text-on-surface text-lg">42</span>
            <span className="text-secondary text-[11px] font-medium">Enrolled</span>
            <span className="text-primary text-[10px] font-semibold mt-0.5">• Full Roster</span>
          </div>

          {/* Bio Indexed */}
          <div className="flex flex-col p-3 rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/30 text-center">
            <div className="flex items-center justify-center text-emerald-600 mb-1">
              <span className="material-symbols-outlined text-[20px]">fingerprint</span>
            </div>
            <span className="font-headline-sm text-headline-sm font-bold text-on-surface text-lg">38/42</span>
            <span className="text-secondary text-[11px] font-medium">Bio Indexed</span>
            <span className="text-emerald-600 text-[10px] font-semibold mt-0.5">90% ready</span>
          </div>

          {/* Avg Attend */}
          <div className="flex flex-col p-3 rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/30 text-center">
            <div className="flex items-center justify-center text-indigo-600 mb-1">
              <span className="material-symbols-outlined text-[20px]">insights</span>
            </div>
            <span className="font-headline-sm text-headline-sm font-bold text-on-surface text-lg">92.8%</span>
            <span className="text-secondary text-[11px] font-medium">Avg Attend</span>
            <span className="text-indigo-600 text-[10px] font-semibold mt-0.5">+3.2% vs wk</span>
          </div>
        </div>

        {/* Hero Card: Live Classroom Attendance */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary to-primary-container p-space-md text-on-primary shadow-lg shadow-primary/20 space-y-space-sm">
          <div className="flex items-center justify-between">
            <span className="px-2 py-0.5 rounded-full bg-surface-container-lowest/20 backdrop-blur-md text-[10px] font-semibold uppercase tracking-wider">
              AI Engine Ready
            </span>
            <span className="material-symbols-outlined text-[24px]">center_focus_strong</span>
          </div>

          <div>
            <h3 className="font-headline-sm text-headline-sm font-bold text-base">
              Live Classroom Attendance
            </h3>
            <p className="font-body-sm text-body-sm text-on-primary-container text-xs mt-1 leading-relaxed">
              Simultaneous multi-face capture using dlib 128-D embedding matrix for B.Tech IT-4A.
            </p>
          </div>

          <button
            type="button"
            onClick={onStartScan}
            className="w-full py-3 px-4 rounded-xl bg-surface-container-lowest text-primary font-semibold text-xs flex items-center justify-center gap-2 shadow-md hover:bg-surface-container transition-all active:scale-95"
          >
            <span className="material-symbols-outlined text-[18px]">center_focus_strong</span>
            <span>Start Multi-Photo AI Scan</span>
          </button>
        </div>

        {/* Quick Administrative Actions */}
        <div className="flex flex-col space-y-space-xs">
          <div className="flex items-center justify-between px-1 text-xs">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-semibold">
              Quick Administrative Actions
            </span>
            <span className="text-secondary">Section IT-A</span>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => onNavigateTab('face-id')}
              className="flex flex-col items-center justify-center p-3 rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/30 hover:border-primary/40 transition-colors"
            >
              <div className="w-9 h-9 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center mb-1">
                <span className="material-symbols-outlined text-[20px]">person_add</span>
              </div>
              <span className="text-xs font-semibold text-on-surface">Face IDs</span>
              <span className="text-[10px] text-amber-700 font-medium">4 Pending</span>
            </button>

            <button
              type="button"
              onClick={() => onNavigateTab('attendance-review')}
              className="flex flex-col items-center justify-center p-3 rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/30 hover:border-primary/40 transition-colors"
            >
              <div className="w-9 h-9 rounded-full bg-indigo-100 text-primary flex items-center justify-center mb-1">
                <span className="material-symbols-outlined text-[20px]">fact_check</span>
              </div>
              <span className="text-xs font-semibold text-on-surface">Drafts</span>
              <span className="text-[10px] text-primary font-medium">1 Unresolved</span>
            </button>

            <button
              type="button"
              onClick={() => onNavigateTab('history')}
              className="flex flex-col items-center justify-center p-3 rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/30 hover:border-primary/40 transition-colors"
            >
              <div className="w-9 h-9 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mb-1">
                <span className="material-symbols-outlined text-[20px]">download</span>
              </div>
              <span className="text-xs font-semibold text-on-surface">Reports</span>
              <span className="text-[10px] text-emerald-700 font-medium">Export CSV</span>
            </button>
          </div>
        </div>

        {/* Last Recorded Lecture Card */}
        <div className="flex flex-col p-space-md rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/30 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-1 font-semibold text-on-surface">
              <span className="material-symbols-outlined text-[16px] text-primary">schedule</span>
              Last Recorded Lecture
            </span>
            <span className="flex items-center gap-1 text-emerald-600 font-semibold text-[11px]">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              Synced
            </span>
          </div>

          <div>
            <div className="text-xs font-bold text-on-surface">Distributed Operating Systems</div>
            <div className="text-[11px] text-secondary">
              Lecture 24 • Consensus Protocols (Paxos &amp; Raft) • Oct 10, 2026
            </div>
          </div>

          <div className="flex items-center gap-3 pt-1 text-xs">
            <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold text-[11px]">
              • 38 Present
            </span>
            <span className="px-2 py-0.5 rounded-full bg-error-container text-on-error-container font-semibold text-[11px]">
              • 4 Absent
            </span>
            <span className="text-secondary font-medium ml-auto">90.5% turnout</span>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-outline-variant/20 text-[11px] text-secondary">
            <span>Engine: Face Recognition dlib 128-D</span>
            <span className="text-primary font-semibold flex items-center gap-0.5">
              <span className="material-symbols-outlined text-[14px]">check</span> Supabase Confirmed
            </span>
          </div>
        </div>
      </div>
    </main>
  );
};
